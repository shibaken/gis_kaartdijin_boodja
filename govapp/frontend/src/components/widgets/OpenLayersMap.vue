<script lang="ts" setup>
  import Map from "ol/Map";
  import View from "ol/View";
  import { onMounted, Ref, ref } from "vue";
  import 'ol/ol.css';
  import { OSM, WMTS } from "ol/source";
  import TileLayer from "ol/layer/Tile";
  import { fromLonLat, transformExtent } from "ol/proj";
  import { LayerSubmission } from "../../providers/layerSubmissionProvider.api";
  import { relatedEntityProvider } from "../../providers/relatedEntityProvider";

  const olMap: Ref = ref(undefined);

  const props = defineProps<{
    submission: LayerSubmission
  }>();

  onMounted(async () => {
    const symbology = await relatedEntityProvider.fetchSymbologies(props.submission.symbology)
    const options = await relatedEntityProvider.fetchWmtsCapabilities(props.submission.name, symbology[0]?.name);

    if (options) {
      const wmts = new WMTS(options),
        extent = wmts.getTileGrid()?.getExtent(),
        projection = wmts.getProjection();

      olMap.value = new Map({
        target: "ol-map",
        layers: [
          new TileLayer({
            source: new OSM(),
            opacity: .7,
          }),
          new TileLayer({
            source: wmts,
            opacity: 1
          }),
        ],
        view: new View({
          center: fromLonLat([122.29833333, -25.32805556], "EPSG:3857"),
          zoom: 5
        })
      });

      if (extent && projection) {
        olMap.value?.getView().fit(transformExtent(extent, projection, olMap.value?.getView().getProjection()));
      }
    }
  });
</script>

<template>
  <div :ref="olMap" id="ol-map"></div>
</template>

<style lang="scss">
  #ol-map {
    height: 30rem;
    max-width: 60rem;
  }
</style>