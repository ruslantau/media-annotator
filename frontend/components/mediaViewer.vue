<!-- Please remove this file from your project -->
<template>
  <div>
    <a-card title="Audio">
      <client-only>
        <vue-wave-surfer ref="surf" :src="file" :options="options" />
        <a-row type="flex" justify="center" style="position: absolute; width: 100%; left:0; bottom: -15px;">
          <a-space size="small" style="position: absolute; left: 0px;">
            <models-tree-select />
          </a-space>
          <a-space size="small">
            <a-popover>
              <div slot="content" style="height: 90px">
                <a-slider
                  vertical
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :default-value="0.5"
                  @afterChange="updateVolumes"
                />
              </div>
              <a-button shape="circle" icon="sound" />
            </a-popover>
            <a-button v-if="!isPlaying" icon="play-circle" type="primary" style="width: 100px;" @click="toggle_play">
              Play
            </a-button>
            <a-button v-else icon="pause-circle" type="primary" style="width: 100px;" @click="toggle_play">
              Pause
            </a-button>
            <a-popover>
              <div slot="content" style="height: 100px">
                <a-slider
                  vertical
                  :min="20"
                  :max="1000"
                  :step="10"
                  :default-value="zoom"
                  @afterChange="updateZoom"
                />
              </div>
              <a-button shape="circle" icon="zoom-in" />
            </a-popover>
          </a-space>
          <a-space size="small" style="position: absolute; right: 0px;">
            <a-button
              icon="delete"
              :type="hovered ? 'danger' : 'default'"
              :loading="isSplitting"
              @mouseover="hovered = true"
              @mouseleave="hovered = false"
              @click="clearRegions"
            >
              Delete all
            </a-button>
            <a-dropdown>
              <a-menu slot="overlay" style="padding: 0;">
                <a-menu-item key="1">
                  As JSON
                </a-menu-item>
                <a-menu-item key="2">
                  As CSV
                </a-menu-item>
                <a-menu-item key="3">
                  As TXT
                </a-menu-item>
              </a-menu>
              <a-button icon="upload" :loading="isExporting">
                Export
              </a-button>
            </a-dropdown>
            <a-button icon="scissor" :loading="isSplitting">
              Split by regions
            </a-button>
            <!--            <a-button icon="edit">Edit</a-button>-->
          </a-space>
        </a-row>
      </client-only>
    </a-card>
    <a-card
      v-if="currentRegion.id !== null"
      style="margin-top: 24px"
      :title="`Annotation for ${currentRegion.start.toFixed(2)}s - ${currentRegion.end.toFixed(2)}s | Region length: ${currentRegion.duration.toFixed(2)}s`"
    >
      <a-form-model layout="inline" :model="currentRegion" @submit.native.prevent>
        <a-row type="flex" :gutter="16">
          <a-col flex="auto">
            <a-input
              v-model="currentRegion.data.text"
              type="textarea"
              placeholder="Text.."
              @change="saveRegion"
              @keyup.delete="saveRegion"
            />
          </a-col>
          <a-col flex="100px">
            <a-row type="flex" justify="center">
              <a-space size="small">
                <a-button icon="delete" type="danger" @click="deleteRegion">
                  Delete
                </a-button>
              </a-space>
            </a-row>
          </a-col>
        </a-row>
      </a-form-model>
    </a-card>
  </div>
</template>

<script>
import Cursor from 'wavesurfer.js/dist/plugin/wavesurfer.cursor'
import Regions from 'wavesurfer.js/dist/plugin/wavesurfer.regions'

export default {
  name: 'NuxtTutorial',
  data () {
    return {
      hovered: false,
      isPlaying: false,
      isExporting: false,
      isSplitting: false,
      file: 'http://localhost:8000/uploads/result_wav.wav',
      zoom: 100,
      currentRegion: {
        id: null,
        start: null,
        end: null,
        duration: null,
        data: { text: null },
        color: null
      },
      options: {
        scrollParent: true,
        regionsMinLength: 1,
        partialRender: true,
        plugins: [
          Cursor.create(),
          Regions.create({
            regionsMinLength: 2,
            dragSelection: {
              slop: 5
            }
          })
        ]
      }
    }
  },
  computed: {
    player () {
      return this.$refs.surf.waveSurfer
    }
  },
  watch: {
    'currentRegion.id': {
      handler (val) {
        if (val !== null) {
          const currentRegion = this.player.regions.list[val]
          this.currentRegion.id = currentRegion.id
          this.currentRegion.start = currentRegion.start
          this.currentRegion.end = currentRegion.end
          this.currentRegion.data.text = currentRegion.data.text
        }
      },
      deep: true
    },
    'currentRegion.end' () {
      this.currentRegion.duration = this.currentRegion.end - this.currentRegion.start
    },
    'currentRegion.start' () {
      this.currentRegion.duration = this.currentRegion.end - this.currentRegion.start
    }
  },
  mounted () {
    this.$nextTick(function () {
      this.$nextTick(function () {
        this.player.on('ready', () => {
          this.player.zoom(this.zoom)
        })
        this.player.on('region-click', (region, e) => {
          e.stopPropagation()
          region.play()
          this.currentRegion.id = region.id
        })
        this.player.on('region-mouseenter', (region, e) => {
          this.currentRegion.id = region.id
        })
        this.player.on('region-updated', (region, e) => {
          this.currentRegion.id = region.id
          this.currentRegion.start = region.start
          this.currentRegion.end = region.end
        })
        this.$nuxt.$on('update-annotations', (newAnnotations, e) => {
          // eslint-disable-next-line
          console.log()
          newAnnotations.forEach((region) => {
            this.player.addRegion(region)
          })
        })
      })
    })
  },
  methods: {
    toggle_play () {
      this.player.playPause()
      this.isPlaying = this.player.isPlaying()
    },
    updateVolumes (value) {
      this.player.setVolume(value)
    },
    updateZoom (value) {
      this.player.zoom(Number(value))
    },
    clearRegions () {
      this.player.clearRegions()
      this.currentRegion.id = null
    },
    saveRegion () {
      if (![undefined, '', ' ', null].includes(this.currentRegion.data.text.trim())) {
        this.player.regions.list[this.currentRegion.id].data.text = this.currentRegion.data.text
        this.player.regions.list[this.currentRegion.id].color = 'rgba(0, 255, 0, 0.1)'
        this.player.regions.list[this.currentRegion.id].element.style.backgroundColor = 'rgba(0, 255, 0, 0.1)'
      } else {
        this.player.regions.list[this.currentRegion.id].data.text = null
        this.player.regions.list[this.currentRegion.id].color = 'rgba(0, 0, 0, 0.1)'
        this.player.regions.list[this.currentRegion.id].element.style.backgroundColor = 'rgba(0, 0, 0, 0.1)'
      }
    },
    deleteRegion () {
      this.player.regions.list[this.currentRegion.id].remove()
      this.currentRegion.id = null
    }
  }
}
</script>
<style>
.wavesurfer-handle {
  width: 2px !important;
}

</style>