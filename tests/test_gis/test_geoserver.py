import unittest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from govapp.gis.geoserver import GeoServer

class TestGeoServerSetDefaultStyle(unittest.TestCase):

    @patch('govapp.gis.geoserver.httpx')
    def test_set_default_style_to_layer_ scenarios(self, mock_httpx):
        # Common setup
        geoserver_instance = GeoServer(service_url="http://dummygeoserver.com/geoserver", username="admin", password="password")
        workspace = "test_workspace"
        layer_name = "test_layer"
        new_style_name = "new_style"
        expected_url = f"{geoserver_instance.service_url}/rest/workspaces/{workspace}/layers/{layer_name}.xml"

        # Mock httpx.get and httpx.put responses
        mock_get_response = MagicMock()
        mock_get_response.raise_for_status = MagicMock()
        
        mock_put_response = MagicMock()
        mock_put_response.raise_for_status = MagicMock()

        # Scenario 1: defaultStyle and name exist
        initial_xml_scenario1 = f"""<layer>
            <name>{layer_name}</name>
            <defaultStyle>
                <name>old_style</name>
            </defaultStyle>
            <resource class="featureType">
                <name>{layer_name}</name>
            </resource>
        </layer>"""
        expected_xml_scenario1 = f"<layer><name>{layer_name}</name><defaultStyle><name>{new_style_name}</name></defaultStyle><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"
        
        # Scenario 2: defaultStyle exists, but no name
        initial_xml_scenario2 = f"""<layer>
            <name>{layer_name}</name>
            <defaultStyle/>
            <resource class="featureType">
                <name>{layer_name}</name>
            </resource>
        </layer>"""
        expected_xml_scenario2 = f"<layer><name>{layer_name}</name><defaultStyle><name>{new_style_name}</name></defaultStyle><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"

        # Scenario 3: defaultStyle does not exist
        initial_xml_scenario3 = f"""<layer>
            <name>{layer_name}</name>
            <resource class="featureType">
                <name>{layer_name}</name>
            </resource>
        </layer>"""
        expected_xml_scenario3 = f"<layer><name>{layer_name}</name><resource class=\"featureType\"><name>{layer_name}</name></resource><defaultStyle><name>{new_style_name}</name></defaultStyle></layer>"
        
        # Scenario 4: defaultStyle and styles exist (styles should be removed)
        initial_xml_scenario4 = f"""<layer>
            <name>{layer_name}</name>
            <defaultStyle>
                <name>old_style</name>
            </defaultStyle>
            <styles>
                <style><name>another_style</name></style>
            </styles>
            <resource class="featureType">
                <name>{layer_name}</name>
            </resource>
        </layer>"""
        expected_xml_scenario4 = f"<layer><name>{layer_name}</name><defaultStyle><name>{new_style_name}</name></defaultStyle><resource class=\"featureType\"><name>{layer_name}</name></resource></layer>"

        scenarios = [
            ("Scenario 1: defaultStyle and name exist", initial_xml_scenario1, expected_xml_scenario1),
            ("Scenario 2: defaultStyle exists, but no name", initial_xml_scenario2, expected_xml_scenario2),
            ("Scenario 3: defaultStyle does not exist", initial_xml_scenario3, expected_xml_scenario3),
            ("Scenario 4: defaultStyle and styles exist", initial_xml_scenario4, expected_xml_scenario4),
        ]

        for description, initial_xml, expected_xml_str in scenarios:
            with self.subTest(description):
                # Reset mocks for each sub-test if necessary, though individual get/put calls are fresh
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
                mock_httpx.get.assert_called_once_with(
                    url=expected_url,
                    auth=(geoserver_instance.username, geoserver_instance.password),
                    headers={"Accept": "application/xml"},
                    timeout=120.0
                )
                mock_get_response.raise_for_status.assert_called_once()

                mock_httpx.put.assert_called_once_with(
                    url=expected_url,
                    content=unittest.mock.ANY,  # Check content separately
                    headers={"Content-Type": "application/xml"},
                    auth=(geoserver_instance.username, geoserver_instance.password),
                    timeout=120.0
                )
                mock_put_response.raise_for_status.assert_called_once()
                
                # Parse and compare XML content
                # This is more robust than string comparison for XML.
                sent_xml_str = mock_httpx.put.call_args[1]['content']
                
                # Normalize XML strings for comparison (optional, but good for handling minor formatting differences)
                # For this test, direct string comparison of canonicalized XML is okay if generated XML is consistent.
                # A more robust way is to parse both and compare ET.Element objects structure and text.
                
                # For simplicity here, we'll compare the string representation after parsing and re-serializing 
                # This helps normalize some minor textual differences if not using a full XML diff tool.
                sent_tree = ET.ElementTree(ET.fromstring(sent_xml_str))
                expected_tree = ET.ElementTree(ET.fromstring(expected_xml_str))

                # Basic check: root tag and defaultStyle name
                sent_root = sent_tree.getroot()
                expected_root = expected_tree.getroot()
                self.assertEqual(sent_root.tag, expected_root.tag)
                
                sent_default_style_name = sent_root.find('.//defaultStyle/name')
                expected_default_style_name = expected_root.find('.//defaultStyle/name')
                self.assertIsNotNone(sent_default_style_name, "defaultStyle/name not found in sent XML")
                self.assertIsNotNone(expected_default_style_name, "defaultStyle/name not found in expected XML")
                self.assertEqual(sent_default_style_name.text, new_style_name)
                self.assertEqual(expected_default_style_name.text, new_style_name)

                # Check if <styles> element is absent in sent XML (as per implementation)
                sent_styles_element = sent_root.find('styles')
                self.assertIsNone(sent_styles_element, "<styles> element should have been removed")

                # Reset mocks for the next iteration
                mock_httpx.get.reset_mock()
                mock_httpx.put.reset_mock()
                mock_get_response.raise_for_status.reset_mock()
                mock_put_response.raise_for_status.reset_mock()

if __name__ == '__main__':
    unittest.main()
