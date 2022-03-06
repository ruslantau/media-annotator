<template>
  <div>
    <media-viewer
      v-if="projectData.data.length > 0"
      ref="mediaViewer"
      :file-url="`http://localhost:8000/uploads/${$router.currentRoute.params.id}/${projectData.data[currentMediaId].file_url}`"
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
      currentMediaURL: null
    }
  },
  async fetch () {
    this.projectData = await fetch('http://localhost:8000' + this.$router.currentRoute.path)
      .then(res => res.json())
  },
  watch: {
    currentMediaId (id) {
      this.currentMediaURL = `http://localhost:8000/uploads/${this.$router.currentRoute.params.id}/${this.projectData.data[this.currentMediaId].file_url}`
      this.$refs.mediaViewer.player.clearRegions()
      this.$refs.mediaViewer.player.empty()
      this.$refs.mediaViewer.player.load(this.currentMediaURL)
      this.$refs.mediaViewer.player.zoom(this.$refs.mediaViewer.zoom - 0.1)
    }
  },
  methods: {
    previousMedia () {
      this.currentMediaId = Math.max(0, this.currentMediaId - 1)
    },
    nextMedia () {
      this.currentMediaId = Math.min(this.currentMediaId + 1, this.projectData.data.length)
    }
  }
}
</script>
