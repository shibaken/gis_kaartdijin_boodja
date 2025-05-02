"""GeoServer Abstractions."""


# Standard
import json
import logging
import pathlib
import requests
from django.template import loader

# Third-Party
from django import conf
import httpx

# Typing
from typing import Any, Optional
from django.template.loader import render_to_string

from govapp.common.utils import handle_http_exceptions

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
    
    @property
    def auth(self):
        return (self.username, self.password)

    @property
    def headers_json(self):
        return {"content-type": "application/json","Accept": "application/json"}

    @handle_http_exceptions(log)
    def retrieve_cached_layer(self, layer_name):
        # Construct URL
        url = f"{self.service_url}/gwc/rest/layers/{layer_name}.json"
        log.info(f'Retrieving cached layer... url: [{url}]')

        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )

        # Check Response
        response.raise_for_status()

        try:
            json_data = response.json()
            formatted_json = json.dumps(json_data, indent=4, sort_keys=True, ensure_ascii=False)
            log.info(f"Cached layer: [{layer_name}] retrieved: [{formatted_json}]")
            return json_data
        except ValueError as e:
            log.error(f"Failed to parse JSON response: {e}")

    @handle_http_exceptions(log)
    def get_list_of_cached_layers(self):
        # Construct URL
        url = f"{self.service_url}/gwc/rest/layers.json"
        log.info(f'Getting the list of cached layers... url: [{url}]')  

        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )

        # Check Response
        response.raise_for_status()

        try:
            json_data = response.json()
            formatted_json = json.dumps(json_data, indent=4, sort_keys=True, ensure_ascii=False)
            log.info(f"List of the cached layers retrieved: [{formatted_json}]")
            return json_data
        except ValueError as e:
            log.error(f"Failed to parse JSON response: {e}")

    @handle_http_exceptions(log)
    def create_or_update_cached_layer(self, layer_name, service_type, create_cached_layer=True, expire_server_cache_after_n_seconds=0, expire_client_cache_after_n_seconds=0):
        from govapp.apps.catalogue.models.catalogue_entries import CatalogueEntryType

        # Construct URL
        url = f"{self.service_url}/gwc/rest/layers/{layer_name}.json"
        log.info(f'Creating/Updating the cached layer... url: [{url}]')
        
        template = loader.get_template('govapp/geoserver/gwc_layer_setting.xml')
        response = httpx.put(
            url=url,
            auth=(self.username, self.password),
            headers={'content-type':'text/xml'},
            data=template.render({
                'layer_name': layer_name,
                'service_type': service_type,
                'create_cached_layer': create_cached_layer,
                'expire_cache': expire_server_cache_after_n_seconds,
                'expire_clients': expire_client_cache_after_n_seconds,
                'CatalogueEntryType': CatalogueEntryType
            })
        )

        response.raise_for_status()

        if response.status_code == 201:
            log.info(f"Cached layer: [{layer_name}] created successfully in the geoserver: [{self.service_url}].")
        elif response.status_code == 200:
            log.info(f"Cached layer: [{layer_name}] updated successfully in the geoserver: [{self.service_url}].")
        else:
            log.error(f"Failed to create/update the cached layer: [{layer_name}] in the geoserver: [{self.service_url}].  {response.status_code} {response.text}")
        # Layer exists, proceed with deletion
    
    @handle_http_exceptions(log)
    def delete_cached_layer(self, layer_name):
        """Delete a cached layer if it exists.
        
        Args:
            layer_name (str): Name of the layer to delete
        """
        # Check if layer exists
        check_url = f"{self.service_url}/gwc/rest/layers/{layer_name}.json"
        log.info(f'Checking if cached layer exists... url: [{check_url}]')
        
        response = httpx.get(
            url=check_url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )
        
        if response.status_code == 404:
            log.info(f"Cached layer: [{layer_name}] does not exist in geoserver: [{self.service_url}].")
            return
            
        # Layer exists, proceed with deletion
        log.info(f"Cached layer: [{layer_name}] exists in geoserver: [{self.service_url}].")
        log.info(f'Deleting the cached layer... url: [{check_url}]')
        response = httpx.delete(
            url=check_url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )
        
        response.raise_for_status()
        log.info(f"Cached layer: [{layer_name}] deleted successfully from the geoserver: [{self.service_url}].")

    @handle_http_exceptions(log)
    def create_store_if_not_exists(self, workspace_name, store_name, data, datastore_type='datastores'):
        # URL to check the existence of the store
        store_get_url = f"{self.service_url}/rest/workspaces/{workspace_name}/{datastore_type}/{store_name}"
        log.info(f'store_get_url: {store_get_url}')

        # Check if Store Exists
        log.info(f'Checking if the store exists...')
        with httpx.Client(auth=(self.username, self.password)) as client:
            response = client.get(store_get_url, headers=self.headers_json)

        # data = data.replace('\n', '')
        # Decide whether to perform a POST or PUT request based on the existence of the store
        if response.status_code == 404: 
            # Store does not exist, perform a POST request
            url = f"{self.service_url}/rest/workspaces/{workspace_name}/{datastore_type}"

            log.info(f'Store: [{store_name}] does not exist. Performing POST request to create the store.')
            log.info(f'POST url: {url}')
            log.info(f'data: {data}')
            with httpx.Client(auth=(self.username, self.password)) as client:
                response = client.post(url=url, headers=self.headers_json, data=data)
        else:
            # Store exists, perform a PUT request
            log.info(f'Store: [{store_name}] exists. Performing PUT request to update the store.')
            log.info(f'PUT url: {store_get_url}')
            log.info(f'data: {data}')
            with httpx.Client(auth=(self.username, self.password)) as client:
                response = client.put(url=store_get_url, headers=self.headers_json, data=data)
            
        return response

    def _stream_file(self, filepath: pathlib.Path, chunk_size: int = 1024 * 1024):
        """Generator function to stream file in chunks.

        Args:
            filepath (pathlib.Path): Path to the file to stream.
            chunk_size (int): Size of chunks to read.

        Yields:
            Generator[bytes, None, None]: File chunks as bytes.
        """
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @handle_http_exceptions(log)
    def upload_geopackage(
        self,
        workspace: str,
        layer: str,
        filepath: pathlib.Path,
        chunk_size: Optional[int] = 1024 * 1024  # 1MB chunks by default
    ) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
            chunk_size (Optional[int]): Size of chunks for streaming upload (default: 1MB)
        """
        log.info(f"Uploading Geopackage '{filepath}' to GeoServer...")

        # Construct URL
        url = f"{self.service_url}/rest/workspaces/{workspace}/datastores/{layer}/file.gpkg"

        # Set appropriate headers for streaming upload
        headers = {
            'Content-Type': 'application/x-gpkg',  # GeoPackage mime type
            'Transfer-Encoding': 'chunked',
            'Connection': 'keep-alive'
        }
        
        # Set query parameters
        params = {
            'filename': filepath.name,
            'update': 'overwrite',
            'configure': 'all'
        }

        # Log file size for monitoring
        file_size = filepath.stat().st_size
        log.info(f"File size: {file_size / (1024*1024):.2f} MB")

        with requests.Session() as session:
            # Perform streaming upload
            try:
                response = session.put(
                    url=url,
                    data=self._stream_file(filepath, chunk_size),
                    params=params,
                    headers=headers,
                    auth=(self.username, self.password),
                    timeout=3000.0,  # 50 minutes timeout
                    stream=True
                )

                log.info(f"GeoServer response: '{response.status_code}: {response.text}'")
                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                log.error(f'Upload failed: [{str(e)}]')
                raise

    @handle_http_exceptions(log)
    def upload_tif(
        self,
        workspace: str,
        layer: str,
        filepath: pathlib.Path,
        chunk_size: Optional[int] = 1024 * 1024  # 1MB chunks by default
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
        url = f"{self.service_url}/rest/workspaces/{workspace}/coveragestores/{layer}/file.geotiff"
        
        headers = {
            'Content-Type': 'image/tiff',
            'Transfer-Encoding': 'chunked',
            'Connection': 'keep-alive'
        }
        
        params = {
            'filename': layer,
            'update': 'overwrite',
            'configure': 'all',
            # 'coverageName': layer
        }

        file_size = filepath.stat().st_size
        log.info(f"File size: {file_size / (1024*1024):.2f} MB")

        with requests.Session() as session:
            # Perform streaming upload
            try:
                response = session.put(
                    url=url,
                    data=self._stream_file(filepath, chunk_size),
                    params=params,
                    headers=headers,
                    auth=(self.username, self.password),
                    timeout=3000.0,
                    stream=True
                )

                log.info(f"GeoServer response: '{response.status_code}: {response.text}'")
                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                log.error(f'Upload failed: [{str(e)}]')
                raise

    @handle_http_exceptions(log)
    def create_layer_from_coveragestore(self, workspace: str, layer: str) -> None:
        """
        Creates a layer in GeoServer from an existing coverage store.

        Args:
            workspace (str): Workspace where the coverage store exists.
            layer (str): Name of the layer to create in GeoServer.
        """
        try:
            response_data = self.get_layer_details(layer)
        except Exception as e:
            log.error(f'Failed to get layer details: [{layer}].  {str(e)}')
            raise
        response_data['layer']['resource']['srs'] = "EPSG:26918"
        response_data['layer']['resource']['boundingBox'] = {
                "nativeBoundingBox": {
                    "minx": -180,
                    "miny": -90,
                    "maxx": 180,
                    "maxy": 90,
                    "crs": "EPSG:26918"
                },
                "latLonBoundingBox": {
                    "minx": -180,
                    "miny": -90,
                    "maxx": 180,
                    "maxy": 90,
                    "crs": "EPSG:26918"
                }
            }
        log.info(f'layer_data: [{response_data}]')
        # Log
        log.info(f"Creating layer '{layer}' in workspace '{workspace}'")

        # Construct URL for layers endpoint
        layers_url = f"{self.service_url}/rest/layers/{workspace}:{layer}.json"

        # Perform POST request to create the layer
        response = httpx.put(
            url=layers_url,
            content=json.dumps(response_data),
            headers=self.headers_json,
            auth=(self.username, self.password),
            timeout=3000.0
        )

        # Log GeoServer response
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check response status
        response.raise_for_status()

    def upload_store_wms(self, workspace, store_name, context) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading WMS Store to GeoServer...")
        
        data = render_to_string('govapp/geoserver/wms/wms_store.json', context)

        response = self.create_store_if_not_exists(workspace, store_name, data, datastore_type='wmsstores')
        
        # Log
        log.info(f"GeoServer WMS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()

    @handle_http_exceptions(log)
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
            
            xml_data = render_to_string('govapp/geoserver/wms/wms_layer.json', context)
            log.info(f'data: { xml_data }')

            layer_get_url = f"{self.service_url}/rest/workspaces/{workspace}/wmsstores/{store_name}/wmslayers/{layer_name}"
            log.info(f'layer_get_url: {layer_get_url}')

            # Check if Layer Exists
            log.info(f'Checking if the layer exists...')
            response = httpx.get(
                url=layer_get_url+"",
                auth=(self.username, self.password),
                headers=self.headers_json,
                timeout=120.0
            )

            log.info(f'Response of the check: { response.status_code }: { response.text }')

            if response.status_code == 200:
                log.info(f"Layer: {layer_name} exists.  Delete it...")
                response = httpx.delete(
                    url=layer_get_url+"?recurse=true",
                    auth=(self.username, self.password),
                    #data=xml_data,
                    headers=self.headers_json,
                    timeout=120.0
                )
            else:
                log.info(f'Layer: {layer_name} does not exist.')

            # Construct URL
            url = f"{self.service_url}/rest/workspaces/{workspace}/wmsstores/{store_name}/wmslayers/"

            log.info(f'Creat the layer by post request...')
            log.info(f'Post url: { url }')
            log.info(f'data: {xml_data}')
            response = httpx.post(
                url=url,
                auth=(self.username, self.password),
                data=xml_data,
                headers=self.headers_json,
                timeout=3000
            )

            log.info(f'Response of the create: { response.status_code }: { response.text }')
            
            # Check Response
            response.raise_for_status()        

    def upload_store_postgis(self, workspace, store_name, context) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading POSTGIS Store to GeoServer...")
        
        data = render_to_string('govapp/geoserver/postgis/postgis_store.json', context)
        # data_update = render_to_string('govapp/geoserver/postgis/postgis_store_update.json', context)

        response = self.create_store_if_not_exists(workspace, store_name, data)

        # Log
        log.info(f"GeoServer POSTGIS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()     

    def upload_store_wfs(self, workspace, store_name, context) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            workspace (str): Workspace to upload files to.
            layer (str): Name of the layer to upload GeoPackage for.
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Log
        log.info(f"Uploading WFS Store to GeoServer")
        
        data = render_to_string('govapp/geoserver/wfs/wfs_store.json', context)
        
        response = self.create_store_if_not_exists(workspace, store_name, data)
        
        # Log
        log.info(f"GeoServer WFS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()    

    @handle_http_exceptions(log)
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
        log.info(f"Uploading WFS/Postgis Layer to GeoServer...")
        
        data_in_json = render_to_string('govapp/geoserver/wfs/wfs_layer.json', context)
        layer_get_url = f"{self.service_url}/rest/workspaces/{workspace}/datastores/{store_name}/featuretypes/{layer_name}"

        # Check if Layer Exists
        response = httpx.get(
            url=layer_get_url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )
        if response.status_code == 200:
            log.info(f'Layer: [{layer_name}] exists.  Perform delete request.')
            response = httpx.delete(
                url=layer_get_url+"?recurse=true",
                auth=(self.username, self.password),
                #data=xml_data,
                headers=self.headers_json,
                timeout=120.0
            )
        else:
            log.info(f'Layer: [{layer_name}] does not exist.')

        # Create the layer
        url = f"{self.service_url}/rest/workspaces/{workspace}/datastores/{store_name}/featuretypes"

        log.info(f'Create the layer by post request...')
        log.info(f'Post url: { url }')
        log.info(f'Post data: {data_in_json}')
        response = httpx.post(
            url=url,
            auth=(self.username, self.password),
            data=data_in_json,
            headers=self.headers_json,
            timeout=300.0
        )
        log.info(f"GeoServer WFS response: '{response.status_code}: {response.text}'")
        
        # Check Response
        response.raise_for_status()

    @handle_http_exceptions(log)
    def upload_style(
        self,
        workspace: str,
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
            url = f"{self.service_url}/rest/workspaces/{workspace}/styles"

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
                timeout=120.0
            )

            # Log
            log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

            # Check Response
            response.raise_for_status()

        # Log
        log.info(f"Uploading Style '{name}' to GeoServer")

        # Upload the Style
        url = f"{self.service_url}/rest/workspaces/{workspace}/styles/{name}.xml"

        # Perform Request
        response = httpx.put(
            url=url,
            content=sld,
            headers={"Content-Type": "application/vnd.ogc.se+xml"},
            auth=(self.username, self.password),
            timeout=120.0
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        response.raise_for_status()

    @handle_http_exceptions(log)
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
        url = f"{self.service_url}/rest/workspaces/{workspace}/styles/{name}.sld"

        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
            timeout=120.0
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        if response.is_success:
            # Return Text
            return response.text

        # Return None
        return None

    @handle_http_exceptions(log)
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
        url = f"{self.service_url}/rest/workspaces/{workspace}/layers/{layer}.xml"

        # Perform Request
        # This only works with XML (GeoServer is broken)
        response = httpx.put(
            url=url,
            content=f"<layer><defaultStyle><name>{name}</name></defaultStyle></layer>",
            headers={"Content-Type": "application/xml"},
            auth=(self.username, self.password),
            timeout=120.0
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        response.raise_for_status()

    @handle_http_exceptions(log)
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
            timeout=120.0
        )

        # Log
        log.info(f"GeoServer response: '{response.status_code}: {response.text}'")

        # Check Response
        if response.is_error:
            # Return JSON
            return response.json()  # type: ignore[no-any-return]

        # Return None
        return None

    @handle_http_exceptions(log)
    def get_layers(self) -> Optional[list[dict[str, str]]]:
        #return None
        """Retreiving layers from GeoServer.

        Returns:
            Optional[list[dict[str, str]]]: A list of layer information
        """
        # Log
        log.info(f'Retreiving layers from GeoServer: [{self.service_url}]')
        
        # Construct URL
        url = "{0}/rest/layers".format(self.service_url)

        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )
        
        # Check Response
        response.raise_for_status()
        
        json_response = response.json()
        if (json_response == None or 
            hasattr(json_response, 'layers') or 
            hasattr(json_response, 'layer')):
            log.error(f"The response of retrieving layers from a GeoServer was wrong. {json_response}")
        # Return JSON
        if json_response['layers']:
            return json_response['layers']['layer']
        else:
            # No layers
            return []

    @handle_http_exceptions(log)
    def get_layer_details(self, layer_name: str) -> Optional[dict]:
        """
        Retrieve details for a specific layer from GeoServer.

        Args:
            layer_name (str): The name of the layer to retrieve details for.

        Returns:
            Optional[dict]: The details of the layer, or None if not found.
        """
        # Log
        log.info(f'Retrieving details for layer: [{layer_name}] from GeoServer: [{self.service_url}]')
        
        # Construct URL
        url = f"{self.service_url}/rest/layers/{layer_name}"
        
        # Perform Request
        response = httpx.get(
            url=url,
            auth=(self.username, self.password),
            headers=self.headers_json,
            timeout=120.0
        )

        # Check Response
        response.raise_for_status()

        json_response = response.json()
        if json_response is None or not json_response.get('layer'):
            log.error(f"The response of retrieving details for layer [{layer_name}] from GeoServer was wrong. {json_response}")
            return None
        
        # Return JSON
        # return json_response['layer']
        return json_response

    @handle_http_exceptions(log)
    def delete_layer(self, layer_name) -> None:
        try:
            layer_details = self.get_layer_details(layer_name)

            # Delete Layer
            url = f"{self.service_url}/rest/layers/{layer_name}"
            response = httpx.delete(
                        url=url,
                        auth=(self.username, self.password),
                        headers=self.headers_json,
                        timeout=120.0
                    )
            # Check Response
            response.raise_for_status()

            if response.status_code == 200:
                log.info(f'Layer: [{layer_name}] deleted successfully from the geoserver: [{self.service_url}].')
            else:
                log.error(f'Failed to delete layer: [{layer_name}].  {response.status_code} {response.text}')

            # Delete store
            workspace_and_layer = layer_details['layer']['resource']['name'].split(':')

            if layer_details['layer']['type'] == 'VECTOR':
                url = f"{self.service_url}/rest/workspaces/{ workspace_and_layer[0] }/datastores/{ workspace_and_layer[1] }"
            else:
                url = f"{self.service_url}/rest/workspaces/{ workspace_and_layer[0] }/coveragestores/{ workspace_and_layer[1] }"

            response = httpx.delete(
                        url=url + '?recurse=true',
                        auth=(self.username, self.password),
                        headers=self.headers_json,
                        timeout=120.0
                    )
            # Check Response
            response.raise_for_status()

        except Exception as e:
            log.error(f'Failed to delete layer: [{layer_name}].  {str(e)}')
            raise


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



