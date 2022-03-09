<template>
  <div>
    <media-viewer
      v-if="projectData.data.length > 0"
      ref="mediaViewer"
      :file-url="`http://localhost:8000/uploads/${$router.currentRoute.params.id}/${projectData.data[currentMediaId].file_url}`"
      :regions="projectData.data[currentMediaId].annotations"
      :input-file-name="`${$router.currentRoute.params.id}/${projectData.data[currentMediaId].file_url}`"
    >
      <div slot="card-extra" style="position: absolute; left: 0; top:0; width: 100%; padding: 12px 0;">
        <a-row type="flex" justify="center" align="middle">
          <a-space>
            <a-button :disabled="currentMediaId === 0" @click="previousMedia">
              <a-icon type="step-backward" />
              Previous
            </a-button>
            <a-select v-model="currentMediaId" :default-value="0" style="max-width: 400px">
              <a-select-option v-for="(data, i) in projectData.data" :key="i" :value="i">
                {{ data.file_url }}
              </a-select-option>
            </a-select>
            <a-button :disabled="currentMediaId === projectData.data.length - 1" @click="nextMedia">
              Next
              <a-icon type="step-forward" />
            </a-button>
          </a-space>
          <a-button style="position: absolute; right: 13px;" icon="save" :loading="isSynchRunned" :disabled="isSynchRunned" @click="saveAnnotations">
            Synchronize all annotations
          </a-button>
        </a-row>
      </div>
    </media-viewer>
  </div>
</template>

<script>
export default {
  name: 'ProjectPage',
  layout: 'base',
  data () {
    return {
      projectData: { data: [] },
      currentMediaId: 0,
      currentMediaURL: null,
      isSynchRunned: false,
      lastSynchronized: null
    }
  },
  async fetch () {
    this.projectData = await fetch('http://localhost:8000' + this.$router.currentRoute.path)
      .then(res => res.json())
  },
  watch: {
    currentMediaId (MediaId) {
      this.currentMediaURL = `http://localhost:8000/uploads/${this.$router.currentRoute.params.id}/${this.projectData.data[MediaId].file_url}`
      this.$refs.mediaViewer.player.clearRegions()
      this.$refs.mediaViewer.player.empty()
      this.$refs.mediaViewer.player.load(this.currentMediaURL)
      this.$refs.mediaViewer.player.zoom(this.$refs.mediaViewer.zoom - 0.1)
      this.projectData.data[MediaId].annotations.forEach((region) => {
        this.$refs.mediaViewer.player.addRegion(this.getRegion(region))
      })
    }
  },
  mounted () {
    this.$nuxt.$on('media-clear-all-regions', (e) => {
      this.projectData.data[this.currentMediaId].annotations = []
    })
    this.$nuxt.$on('media-remove-region', (regionID, e) => {
      const idToRemove = this.projectData.data[this.currentMediaId].annotations.findIndex(ob => ob.id === regionID)
      this.projectData.data[this.currentMediaId].annotations.splice(idToRemove, 1)
    })
    this.$nuxt.$on('media-update-annotations', (newAnnotations, e) => {
      this.projectData.data[this.currentMediaId].annotations = [...newAnnotations.map((region) => {
        this.$refs.mediaViewer.player.addRegion(region)
        return this.getRegion(region)
      })]
    })
    this.$nuxt.$on('media-region-updated', (newRegion, e) => {
      const annotationID = this.projectData.data[this.currentMediaId].annotations.findIndex(obj => obj.id === newRegion.id)
      if (annotationID === -1) {
        this.projectData.data[this.currentMediaId].annotations.push(this.getRegion(newRegion))
      }
      this.projectData.data[this.currentMediaId].annotations[annotationID] = this.getRegion(newRegion)
    })
    this.$nuxt.$on('download-all-annotations', (fileType, e) => {
      if (fileType === 'json') {
        const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.projectData.data))
        const downloadAnchorNode = document.createElement('a')
        downloadAnchorNode.setAttribute('href', dataStr)
        downloadAnchorNode.setAttribute('download', 'annotations.json')
        document.body.appendChild(downloadAnchorNode) // required for firefox
        downloadAnchorNode.click()
        downloadAnchorNode.remove()
      }
    })
  },
  methods: {
    previousMedia () {
      this.currentMediaId = Math.max(0, this.currentMediaId - 1)
    },
    nextMedia () {
      this.currentMediaId = Math.min(this.currentMediaId + 1, this.projectData.data.length)
    },
    async saveAnnotations () {
      this.isSynchRunned = true
      await fetch(`http://localhost:8000/projects/${this.$router.currentRoute.params.id}/annotations`, {
        method: 'PUT',
        body: JSON.stringify(this.projectData.data)
      })
        .then(() => {
          this.lastSynchronized = true
        })
        .catch((e) => {
          // this.lastSynchronized = false
        })
        .finally(() => {
          this.isSynchRunned = false
        })
    },
    getRegion (region) {
      return {
        id: region.id,
        start: region.start,
        end: region.end,
        data: { text: region.data.text },
        color: [undefined, '', ' ', null].includes((region.data.text || '').trim()) ? 'rgba(0, 0, 0, 0.1)' : 'rgba(0, 255, 0, 0.1)'
      }
    }
  }
}
</script>
