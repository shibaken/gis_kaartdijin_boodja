import unittest
from unittest.mock import patch, MagicMock, call
import xml.etree.ElementTree as ET
import logging # For checking log messages
from govapp.gis.geoserver import GeoServer # Assuming GeoServer is in this path
import httpx # For httpx.RequestError

# Configure logging to DEBUG to capture all relevant messages for tests
# This can be done globally or on a per-test basis if needed
logging.basicConfig(level=logging.DEBUG)


class TestGeoServerSetDefaultStyle(unittest.TestCase):

    @patch.object(GeoServer, 'truncate_gwc_layer_cache')
    @patch('govapp.gis.geoserver.httpx') # Patching httpx where it's used in geoserver.py
    def test_set_default_style_to_layer_scenarios(self, mock_httpx, mock_truncate_gwc):
        # Common setup
        geoserver_instance = GeoServer(service_url="http://dummygeoserver.com/geoserver", username="admin", password="password")
        workspace = "test_workspace"
        layer_name = "test_layer"
        new_style_name = "new_style"
        expected_layer_url = f"{geoserver_instance.service_url}/rest/workspaces/{workspace}/layers/{layer_name}.xml"

        # Mock httpx.get and httpx.put responses
        mock_get_response = MagicMock()
        mock_get_response.raise_for_status = MagicMock()
        
        mock_put_response = MagicMock()
        mock_put_response.raise_for_status = MagicMock()

        # XML Scenarios
        initial_xml_scenario1 = f"<layer><name>{layer_name}</name><defaultStyle><name>old_style</name></defaultStyle><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"
        expected_xml_scenario1 = f"<layer><name>{layer_name}</name><defaultStyle><name>{new_style_name}</name></defaultStyle><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"
        initial_xml_scenario4 = f"<layer><name>{layer_name}</name><defaultStyle><name>old_style</name></defaultStyle><styles><style><name>another_style</name></style></styles><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"
        expected_xml_scenario4 = f"<layer><name>{layer_name}</name><defaultStyle><name>{new_style_name}</name></defaultStyle><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"

        xml_scenarios = [
            ("Scenario 1: defaultStyle and name exist", initial_xml_scenario1, expected_xml_scenario1),
            ("Scenario 4: defaultStyle and styles exist", initial_xml_scenario4, expected_xml_scenario4), # Simplified for brevity
        ]

        truncate_outcomes = [True, False] # Test for both GWC truncation outcomes

        for description, initial_xml, expected_xml_str in xml_scenarios:
            for truncate_outcome in truncate_outcomes:
                subtest_description = f"{description} (GWC Truncate: {truncate_outcome})"
                with self.subTest(subtest_description):
                    # Reset mocks for each sub-test
                    mock_httpx.reset_mock()
                    mock_truncate_gwc.reset_mock()
                    mock_get_response.reset_mock()
                    mock_put_response.reset_mock()
                    mock_get_response.raise_for_status.reset_mock()
                    mock_put_response.raise_for_status.reset_mock()
                    
                    mock_truncate_gwc.return_value = truncate_outcome
                    mock_httpx.get.return_value = mock_get_response
                    mock_httpx.put.return_value = mock_put_response
                    mock_get_response.text = initial_xml

                    # Call the method
                    geoserver_instance.set_default_style_to_layer(
                        workspace=workspace,
                        layer=layer_name,
                        style_name=new_style_name
                    )

                    # Assertions
                    mock_truncate_gwc.assert_called_once_with(workspace, layer_name)
                    
                    mock_httpx.get.assert_called_once_with(
                        url=expected_layer_url,
                        auth=(geoserver_instance.username, geoserver_instance.password),
                        headers={"Accept": "application/xml"},
                        timeout=120.0
                    )
                    mock_get_response.raise_for_status.assert_called_once()

                    mock_httpx.put.assert_called_once_with(
                        url=expected_layer_url,
                        content=unittest.mock.ANY,
                        headers={"Content-Type": "application/xml"},
                        auth=(geoserver_instance.username, geoserver_instance.password),
                        timeout=120.0
                    )
                    mock_put_response.raise_for_status.assert_called_once()
                    
                    sent_xml_str = mock_httpx.put.call_args[1]['content']
                    sent_tree = ET.ElementTree(ET.fromstring(sent_xml_str))
                    expected_tree = ET.ElementTree(ET.fromstring(expected_xml_str))
                    sent_root = sent_tree.getroot()
                    expected_root = expected_tree.getroot()
                    self.assertEqual(sent_root.tag, expected_root.tag)
                    sent_default_style_name = sent_root.find('.//defaultStyle/name')
                    self.assertIsNotNone(sent_default_style_name)
                    self.assertEqual(sent_default_style_name.text, new_style_name)
                    sent_styles_element = sent_root.find('styles')
                    self.assertIsNone(sent_styles_element)


class TestGeoServerTruncateGWCCache(unittest.TestCase):

    def setUp(self):
        self.geoserver_instance = GeoServer(service_url="http://dummygeoserver.com/geoserver", username="admin", password="password")
        self.workspace = "test_ws"
        self.layer_name = "test_lyr"
        self.gwc_layer_name = f"{self.workspace}:{self.layer_name}"
        self.expected_gwc_url = f"{self.geoserver_instance.service_url.rstrip('/')}/gwc/rest/seed/{self.gwc_layer_name}.xml"
        self.expected_payload = f"<seedRequest><name>{self.gwc_layer_name}</name><type>truncate</type></seedRequest>"

    @patch('govapp.gis.geoserver.httpx.post')
    @patch('govapp.gis.geoserver.log') # Patching the logger instance used in geoserver.py
    def test_truncate_success_200(self, mock_log, mock_httpx_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_httpx_post.return_value = mock_response

        result = self.geoserver_instance.truncate_gwc_layer_cache(self.workspace, self.layer_name)

        self.assertTrue(result)
        mock_httpx_post.assert_called_once_with(
            url=self.expected_gwc_url,
            content=self.expected_payload,
            headers={"Content-Type": "application/xml"},
            auth=self.geoserver_instance.auth,
            timeout=120.0
        )
        mock_log.info.assert_any_call(f"GWC cache truncation task submitted successfully for '{self.gwc_layer_name}'. Response: 200")


    @patch('govapp.gis.geoserver.httpx.post')
    @patch('govapp.gis.geoserver.log')
    def test_truncate_not_found_404(self, mock_log, mock_httpx_post):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_httpx_post.return_value = mock_response

        result = self.geoserver_instance.truncate_gwc_layer_cache(self.workspace, self.layer_name)

        self.assertTrue(result) # 404 is treated as success (nothing to truncate)
        mock_httpx_post.assert_called_once_with(
            url=self.expected_gwc_url,
            content=self.expected_payload,
            headers={"Content-Type": "application/xml"},
            auth=self.geoserver_instance.auth,
            timeout=120.0
        )
        mock_log.info.assert_any_call(f"GWC layer '{self.gwc_layer_name}' not found, no cache to truncate. Response: 404")

    @patch('govapp.gis.geoserver.httpx.post')
    @patch('govapp.gis.geoserver.log')
    def test_truncate_server_error_500(self, mock_log, mock_httpx_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_httpx_post.return_value = mock_response

        result = self.geoserver_instance.truncate_gwc_layer_cache(self.workspace, self.layer_name)

        self.assertFalse(result)
        mock_httpx_post.assert_called_once_with(
            url=self.expected_gwc_url,
            content=self.expected_payload,
            headers={"Content-Type": "application/xml"},
            auth=self.geoserver_instance.auth,
            timeout=120.0
        )
        mock_log.error.assert_any_call(f"GWC cache truncation for '{self.gwc_layer_name}' failed. Status: 500, Response: Server Error")

    @patch('govapp.gis.geoserver.httpx.post')
    @patch('govapp.gis.geoserver.log')
    def test_truncate_request_error(self, mock_log, mock_httpx_post):
        mock_httpx_post.side_effect = httpx.RequestError("Connection failed", request=MagicMock())

        result = self.geoserver_instance.truncate_gwc_layer_cache(self.workspace, self.layer_name)

        self.assertFalse(result)
        mock_httpx_post.assert_called_once_with(
            url=self.expected_gwc_url,
            content=self.expected_payload,
            headers={"Content-Type": "application/xml"},
            auth=self.geoserver_instance.auth,
            timeout=120.0
        )
        mock_log.error.assert_any_call(unittest.mock.ANY) # Check that some error was logged
        # More specific log check:
        self.assertTrue(any("HTTPX RequestError during GWC cache truncation" in s_call[0][0] for s_call in mock_log.error.call_args_list))


if __name__ == '__main__':
    unittest.main()
