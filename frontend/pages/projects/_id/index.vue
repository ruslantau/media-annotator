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
            <a-button :disabled="currentMediaId === 0 || !isMediaReady" @click="previousMedia">
              <a-icon type="step-backward" />
              Previous
            </a-button>
            <a-select v-model="currentMediaId" :disabled="!isMediaReady" :default-value="0" style="max-width: 400px">
              <a-select-option v-for="(data, i) in projectData.data" :key="i" :value="i">
                {{ data.file_url }}
              </a-select-option>
            </a-select>
            <a-button :disabled="currentMediaId === projectData.data.length - 1 || !isMediaReady" @click="nextMedia">
              Next
              <a-icon type="step-forward" />
            </a-button>
          </a-space>
          <div style="position: absolute; right: 13px;">
            <span style="margin: 0 5px;"><a-icon type="clock-circle" /> {{ lastSyncTimeForHuman }}</span>
            <a-button
              icon="cloud-upload"
              :loading="isSynchRunned"
              :disabled="isSynchRunned || !isMediaReady"
              @click="syncAnnotations"
            >
              Synchronize all
            </a-button>
          </div>
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
      isMediaReady: false,
      lastSyncTime: new Date(),
      lastSyncTimeForHuman: 0
    }
  },
  async fetch () {
    this.projectData = await fetch('http://localhost:8000' + this.$router.currentRoute.path)
      .then(res => res.json())
  },
  watch: {
    currentMediaId (MediaId) {
      this.isMediaReady = false
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
  created () {
    setInterval(this.getLastSyncTime, 1000)
  },
  mounted () {
    this.$nuxt.$on('media-is-ready', (ready) => {
      this.isMediaReady = ready
    })
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
      let dataStr = `data:text/${fileType};charset=utf-8,`
      if (fileType === 'json') {
        dataStr += encodeURIComponent(JSON.stringify(this.projectData.data))
      }
      if (fileType === 'csv') {
        let csvFile = ''
        this.projectData.data.forEach((media) => {
          let csvLine = ''
          // eslint-disable-next-line
          const [filePath, fileExt] = media.file_url.split('.')
          media.annotations.forEach((region) => {
            csvLine += `${filePath}_region_${region.start.toFixed(2)}_${region.end.toFixed(2)}.wav|${region.data.text}\r\n`
          })
          csvFile += csvLine
        })
        dataStr += csvFile
      }
      const downloadAnchorNode = document.createElement('a')
      downloadAnchorNode.setAttribute('href', dataStr)
      downloadAnchorNode.setAttribute('download', `${this.projectData.name}_annotations.${fileType}`)
      document.body.appendChild(downloadAnchorNode) // required for firefox
      downloadAnchorNode.click()
      downloadAnchorNode.remove()
    })
  },
  methods: {
    previousMedia () {
      this.currentMediaId = Math.max(0, this.currentMediaId - 1)
    },
    nextMedia () {
      this.currentMediaId = Math.min(this.currentMediaId + 1, this.projectData.data.length)
    },
    async syncAnnotations () {
      this.isSynchRunned = true
      await fetch(`http://localhost:8000/projects/${this.$router.currentRoute.params.id}/annotations`, {
        method: 'PUT',
        body: JSON.stringify(this.projectData.data)
      })
        .then(() => {
          this.lastSyncTime = new Date()
          this.$message.success('All synchronized now.')
        })
        .catch((e) => {
          this.$message.error('Sync was failed.' + e)
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
    },
    getLastSyncTime () {
      const delta = ~~((new Date() - this.lastSyncTime) / 1000)
      const minutes = ~~(delta / 60)

      if (delta < 60) {
        this.lastSyncTimeForHuman = 'Less than minute'
      }
      if (delta >= 60) {
        this.lastSyncTimeForHuman = `Sync ${minutes}m ago`
      }
    }
  }
}
</script>
