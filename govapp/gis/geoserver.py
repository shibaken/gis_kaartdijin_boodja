"""GeoServer Abstractions."""


# Standard
import logging
import pathlib

# Third-Party
from django import conf
import httpx

# Typing
from typing import Any, Optional
from django.template.loader import render_to_string

# Logging
log = logging.getLogger(__name__)


class GeoServer:
    """GeoServer Abstraction."""

    def __init__(
        self,
        service_url: str,
        username: str,
        password: str,
    ) -> None:
        """Instantiates the GeoServer Abstraction.

        Args:
            service_url (str): URL to the GeoServer service.
            username (str): Username for the GeoServer service.
            password (str): Password for the GeoServer service.
        """
        # Instance Attributes
        self.service_url = service_url
        self.username = username
        self.password = password

        # Strip Trailing Slash from Service URL
        self.service_url = self.service_url.rstrip("/")

    def upload_geopackage(
        self,
        workspace: str,
        layer: str,
        filepath: pathlib.Path,
    ) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading Geopackage '{filepath}' to GeoServer")

        # Construct URL
        url = "{0}/rest/workspaces/{1}/datastores/{2}/file.gpkg".format(
            self.service_url,
            workspace,
            layer,
        )

        # Perform Request
        response = httpx.put(
            url=url,
            content=filepath.read_bytes(),
            params={"filename": filepath.name, "update": "overwrite"},
            auth=(self.username, self.password),
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        response.raise_for_status()

    def upload_tif(
        self,
        workspace: str,
        layer: str,
        filepath: pathlib.Path,
    ) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading GeoTiff '{filepath}' to GeoServer")

        # Construct URL
        url = "{0}/rest/workspaces/{1}/coveragestores/{2}/file.geotiff".format(
            self.service_url,
            workspace,
            layer,
        )

        # Perform Request
        response = httpx.put(
            url=url,
            content=filepath.read_bytes(),
            params={"filename": filepath.name, "update": "overwrite"},
            auth=(self.username, self.password),
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        response.raise_for_status()


    def upload_store_wms(
        self,
        workspace,
        store_name,
        context
    ) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading WMS Store to GeoServer...")
        
        xml_data = render_to_string('govapp/geoserver/wms/wms_store.json', context)

        store_get_url = "{0}/rest/workspaces/{1}/wmsstores/{2}".format(
            self.service_url,
            workspace,
            store_name
        )
        log.info(f'store_get_url: {store_get_url}')

        # Check if Store Exists
        log.info(f'Checking if the store exists...')
        response = httpx.get(
            url=store_get_url,
            auth=(self.username, self.password),
            headers={"content-type": "application/json","Accept": "application/json"}
        )

        # Construct URL
        url = "{0}/rest/workspaces/{1}/wmsstores".format(
            self.service_url,
            workspace
        )

        if response.status_code == 404: 
            # Perform Request
            log.info(f'Store does not exist.  Perform post request.')
            log.info(f'Post url: { url }')
            log.debug(f'xml_data: { xml_data }')
            response = httpx.post(
                url=url,
                auth=(self.username, self.password),
                data=xml_data,
                headers={"content-type": "application/json","Accept": "application/json"}
            )
        else:          
            # Perform Request
            log.info(f'Store exists.  Perform put request.')
            log.info(f'Put url: { store_get_url }')
            log.debug(f'xml_data: { xml_data }')
            response = httpx.put(
                url=store_get_url,
                auth=(self.username, self.password),
                data=xml_data,
                headers={"content-type": "application/json","Accept": "application/json"}
            )

        
        # Log
        log.info(f"GeoServer WMS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()


    def upload_layer_wms(
            self,
            workspace,
            store_name,
            layer_name,
            context
        ) -> None:
            """Uploads a Geopackage file to the GeoServer.

            Args:
                workspace (str): Workspace to upload files to.
                layer (str): Name of the layer to upload GeoPackage for.
                filepath (pathlib.Path): Path to the Geopackage file to upload.
            """
            # Log
            log.info(f"Uploading WMS Layer to GeoServer...")
            # context['native_name'] = 'kaartdijin-boodja-public:CPT_DBCA_OFFICES'
            
            xml_data = render_to_string('govapp/geoserver/wms/wms_layer.json', context)
            log.info(f'xml_data: { xml_data }')

            layer_get_url = "{0}/rest/workspaces/{1}/wmsstores/{2}/wmslayers/{3}".format(
                self.service_url,
                workspace,
                store_name,
                layer_name
            )
            log.info(f'layer_get_url: {layer_get_url}')

            # Check if Layer Exists
            log.info(f'Checking if the layer exists...')
            response = httpx.get(
                url=layer_get_url+"",
                auth=(self.username, self.password),
                headers={"content-type": "application/json","Accept": "application/json"}
            )

            log.info(f'Response of the check: { response.status_code }: { response.text }')

            if response.status_code == 200:
                log.info("Layer exists.  Delete it...")
                response = httpx.delete(
                    url=layer_get_url+"?recurse=true",
                    auth=(self.username, self.password),
                    #data=xml_data,
                    headers={"content-type": "application/json","Accept": "application/json"}
                )

            # Construct URL
            url = "{0}/rest/workspaces/{1}/wmsstores/{2}/wmslayers/".format(
                self.service_url,
                workspace,
                store_name
            )

            log.info(f'Creat the layer by post request...')
            log.info(f'Post url: { url }')
            response = httpx.post(
                url=url,
                auth=(self.username, self.password),
                data=xml_data,
                headers={"content-type": "application/json","Accept": "application/json"},
                timeout=3000
            )

            # if response.status_code == 404: 
            #     # Perform Request
            #     response = httpx.post(
            #         url=url,
            #         auth=(self.username, self.password),
            #         data=xml_data,
            #         headers={"content-type": "application/json","Accept": "application/json"}
            #     )
            #     print ("404")
            #     print (response.text)
            # else:          
            #     # Perform Request
            #     response = httpx.put(
            #         url=store_get_url,
            #         auth=(self.username, self.password),
            #         data=xml_data,
            #         headers={"content-type": "application/json","Accept": "application/json"}
            #     )

            # log.info(response.text)
            
            # Log
            log.info(f'{xml_data}')
            log.info(f'Response of the create: { response.status_code }: { response.text }')
            # log.info(f"GeoServer WMS response: '{response.status_code}: {response.text}'")
            
            # Check Response
            response.raise_for_status()        






    def upload_store_postgis(
        self,
        workspace,
        store_name,
        context
    ) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading POSTGIS Store to GeoServer...")
        
        json_data = render_to_string('govapp/geoserver/postgis/postgis_store.json', context)

        store_get_url = "{0}/rest/workspaces/{1}/datastores/{2}".format(
            self.service_url,
            workspace,
            store_name
        )
        log.info(f'Check if the store exists...')
        log.info(f'GET url: { store_get_url }')
        # Check if Store Exists
        response = httpx.get(
            url=store_get_url,
            auth=(self.username, self.password),
            headers={"content-type": "application/json","Accept": "application/json"}
        )

        # Construct URL
        url = "{0}/rest/workspaces/{1}/datastores".format(
            self.service_url,
            workspace
        )

        if response.status_code == 404: 
            # Perform Request
            log.info(f'Store does not exist.  Perform post request.')
            log.info(f'Post url: { url }')
            log.debug(f'json_data: { json_data }')
            response = httpx.post(
                url=url,
                auth=(self.username, self.password),
                data=json_data,
                headers={"content-type": "application/json","Accept": "application/json"}
            )
        else:  
            #Perform Request
            log.info(f'Store exists.  Perform put request.')
            log.info(f'Put url: { store_get_url }')
            log.debug(f'json_data: { json_data }')
            response = httpx.put(
                url=store_get_url,
                auth=(self.username, self.password),
                data=json_data,
                headers={"content-type": "application/json","Accept": "application/json"}
            )

        
        # Log
        log.info(f"GeoServer POSTGIS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()     



    def upload_store_wfs(
        self,
        workspace,
        store_name,
        context
    ) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading WFS Store to GeoServer")
        
        json_data = render_to_string('govapp/geoserver/wfs/wfs_store.json', context)

        store_get_url = "{0}/rest/workspaces/{1}/datastores/{2}".format(
            self.service_url,
            workspace,
            store_name
        )
        #Check if Store Exists
        response = httpx.get(
            url=store_get_url,
            auth=(self.username, self.password),
            headers={"content-type": "application/json","Accept": "application/json"}
        )
        # Construct URL
        url = "{0}/rest/workspaces/{1}/datastores".format(
            self.service_url,
            workspace
        )

        if response.status_code == 404: 
            # Perform Request
            response = httpx.post(
                url=url,
                auth=(self.username, self.password),
                data=json_data,
                headers={"content-type": "application/json","Accept": "application/json"}
            )
        else:  
            pass        
            #Perform Request
            response = httpx.put(
                url=store_get_url,
                auth=(self.username, self.password),
                data=json_data,
                headers={"content-type": "application/json","Accept": "application/json"}
            )
        
        # Log
        log.info(f"GeoServer WFS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()    


    def upload_layer_wfs(
            self,
            workspace,
            store_name,
            layer_name,
            context
        ) -> None:
            """Uploads a Geopackage file to the GeoServer.

            Args:
                workspace (str): Workspace to upload files to.
                layer (str): Name of the layer to upload GeoPackage for.
                filepath (pathlib.Path): Path to the Geopackage file to upload.
            """
            # Log
            log.info(f"Uploading WFS Layer to GeoServer")
            
            xml_data = render_to_string('govapp/geoserver/wfs/wfs_layer.json', context)
            log.debug(f'xml_data: {xml_data}')

            store_get_url = "{0}/rest/workspaces/{1}/datastores/{2}/featuretypes/{3}".format(
                self.service_url,
                workspace,
                store_name,
                layer_name
            )
            # Check if Store Exists
            response = httpx.get(
                url=store_get_url+"",
                auth=(self.username, self.password),
                headers={"content-type": "application/json","Accept": "application/json"}
            )

            print ("GET WFS LAYER")
            print (response.text)
            print (response.status_code)
            # Construct URL
            url = "{0}/rest/workspaces/{1}/datastores/{2}/featuretypes".format(
                self.service_url,
                workspace,
                store_name
            )
            if response.status_code == 200:
                print ("deleting")
                response = httpx.delete(
                    url=store_get_url+"?recurse=true",
                    auth=(self.username, self.password),
                    #data=xml_data,
                    headers={"content-type": "application/json","Accept": "application/json"}
                )

            response = httpx.post(
                url=url,
                auth=(self.username, self.password),
                data=xml_data,
                # data=request_body,
                headers={"content-type": "application/json","Accept": "application/json"},
                timeout=300.0
            )
            print ("404")
            print (response.text)
            
            # Log
            log.info(f"GeoServer WFS response: '{response.status_code}: {response.text}'")
            
            # Check Response
            response.raise_for_status()        

    def upload_style(
        self,
        workspace: str,
        layer: str,
        name: str,
        sld: str,
    ) -> None:
        """Uploads an SLD Style to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload style for.
            name (str): Name of the style.
            sld (str): Style to upload.
        """
        # Retrieve Existing Style
        existing_sld = self.get_style(workspace, name)

        # Check if Style Exists
        if existing_sld is None:
            # Log
            log.info(f"Creating Style '{name}' in GeoServer")

            # Create the Style
            url = "{0}/rest/workspaces/{1}/styles".format(
                self.service_url,
                workspace,
            )

            # Perform Request
            response = httpx.post(
                url=url,
                json={
                    "style": {
                        "name": name,
                        "filename": f"{name}.sld"
                    }
                },
                auth=(self.username, self.password),
            )

            # Log
            log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

            # Check Response
            response.raise_for_status()

        # Log
        log.info(f"Uploading Style '{name}' to GeoServer")

        # Upload the Style
        url = "{0}/rest/workspaces/{1}/styles/{2}.xml".format(
            self.service_url,
            workspace,
            name,
        )

        # Perform Request
        response = httpx.put(
            url=url,
            content=sld,
            headers={"Content-Type": "application/vnd.ogc.se+xml"},
            auth=(self.username, self.password),
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        response.raise_for_status()

    def get_style(
        self,
        workspace: str,
        name: str,
    ) -> Optional[str]:
        """Retrieves a style from the GeoServer if it exists.

        Args:
            workspace (str): Workspace to upload files to.
            name (str): Name of the style to retrieve.

        Returns:
            Optional[str]: The XML SLD if the style exists, otherwise None.
        """
        # Log
        log.info(f"Checking Style '{name}' existence in GeoServer")

        # Construct URL
        url = "{0}/rest/workspaces/{1}/styles/{2}.sld".format(
            self.service_url,
            workspace,
            name,
        )

        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        if response.is_success:
            # Return Text
            return response.text

        # Return None
        return None

    def set_default_style(
        self,
        workspace: str,
        layer: str,
        name: str,
    ) -> None:
        """Sets the default style for a layer in GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to set default style for.
            name (str): Name of the style.
        """
        # Log
        log.info(f"Setting style '{name}' as default for '{layer}' in GeoServer")

        # Set Default Layer Style
        url = "{0}/rest/workspaces/{1}/layers/{2}.xml".format(
            self.service_url,
            workspace,
            layer,
        )

        # Perform Request
        # This only works with XML (GeoServer is broken)
        response = httpx.put(
            url=url,
            content=f"<layer><defaultStyle><name>{name}</name></defaultStyle></layer>",
            headers={"Content-Type": "application/xml"},
            auth=(self.username, self.password),
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        response.raise_for_status()

    def validate_style(self, sld: str) -> Optional[dict[str, Any]]:
        #return None
        """Validates SLD using the GeoServer OGC API.

        Args:
            sld (str): Style to validate.

        Returns:
            Optional[dict[str, Any]]: JSON of errors if applicable, otherwise
                None.
        """
        # Log
        log.info("Validating Style in GeoServer")

        # Construct URL
        url = "{0}/ogc/styles/styles".format(self.service_url)

        # Perform Request
        response = httpx.post(
            url=url,
            auth=(self.username, self.password),
            content=sld,
            params={"validate": "only"},
            headers={"Content-Type": "application/vnd.ogc.se+xml"},
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        if response.is_error:
            # Return JSON
            return response.json()  # type: ignore[no-any-return]

        # Return None
        return None


    def get_layers(self) -> Optional[list[dict[str, str]]]:
        #return None
        """Retreiving layers from GeoServer.

        Returns:
            Optional[list[dict[str, str]]]: A list of layer information
        """
        # Log
        log.info("Retreiving layers from GeoServer")
        
        # Construct URL
        url = "{0}/rest/layers".format(self.service_url)

        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
            headers={"content-type": "application/json","Accept": "application/json"},
        )
        
        # Check Response
        response.raise_for_status()
        
        json_response = response.json()
        if (json_response == None or 
            hasattr(json_response, 'layers') or 
            hasattr(json_response, 'layer')):
            log.error(f"The response of retrieving layers from a GeoServer was wrong. {json_response}")
        # Return JSON
        return json_response['layers']['layer']
    
    
    def delete_layer(self, layer_name) -> None:
        # Construct URL
        url = "{0}/rest/layers/{1}".format(
            self.service_url,
            layer_name
            )
        
        response = httpx.delete(
                    url=url,
                    auth=(self.username, self.password),
                    #data=xml_data,
                    headers={"content-type": "application/json","Accept": "application/json"}
                )
        
        # Check Response
        response.raise_for_status()
        

def geoserver() -> GeoServer:
    """Helper constructor to instantiate GeoServer.

    Returns:
        GeoServer: Configured GeoServer instance.
    """
    # Construct and Return
    return GeoServer(
        service_url=conf.settings.GEOSERVER_URL,
        username=conf.settings.GEOSERVER_USERNAME,
        password=conf.settings.GEOSERVER_PASSWORD,
    )


def geoserverWithCustomCreds(url,username,password):
    return GeoServer(
        service_url=url,
        username=username,
        password=password,
    )



