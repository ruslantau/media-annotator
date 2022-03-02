<!-- Please remove this file from your project -->
<template>
  <div>
    <a-card title="Audio">
      <client-only>
        <vue-wave-surfer ref="surf" :src="file" :options="options" />
        <a-row type="flex" justify="center" style="position: absolute; width: 100%; left:0; bottom: -15px;">
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
            <a-button icon="coffee" :loading="isAnnotating">Auto annotation</a-button>
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
              <a-button icon="upload" :loading="isExporting">Export</a-button>
            </a-dropdown>
            <a-button icon="scissor" :loading="isSplitting">Split by regions</a-button>
            <!--            <a-button icon="edit">Edit</a-button>-->
          </a-space>
        </a-row>
      </client-only>
    </a-card>
    <a-card
      v-if="currentRegionId !== undefined"
      style="margin-top: 24px"
      :title="`Annotation for ${~~currentRegion.start}s - ${~~currentRegion.end}s | Region length: ${~~currentRegion.end}`"
    >
      <a-form-model ref="regionForm" layout="inline" :model="currentRegion" @submit.native.prevent>
        <a-row type="flex" :gutter="16">
          <a-col flex="auto">
            <a-input
              v-model.lazy="currentRegion.text"
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
      isPlaying: false,
      isAnnotating: false,
      isExporting: false,
      isSplitting: false,
      file: 'http://localhost:8000/uploads/result_wav.wav',
      zoom: 100,
      currentRegionId: undefined,
      currentRegion: {},
      options: {
        scrollParent: true,
        regionsMinLength: 1,
        plugins: [
          Cursor.create(),
          Regions.create({
            regionsMinLength: 2,
            regions: [],
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
    },
    regionForm () {
      return this.$refs.regionForm
    }
  },
  watch: {
    currentRegionId (val) {
      if (val !== undefined) {
        const currentRegion = this.player.regions.list[val]
        this.currentRegion.id = currentRegion.id
        this.currentRegion.start = currentRegion.start
        this.currentRegion.end = currentRegion.end
        this.currentRegion.text = currentRegion.text
      }
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
          this.currentRegionId = region.id
        })
        this.player.on('region-mouseenter', (region, e) => {
          this.currentRegionId = region.id
        })
        this.player.on('region-update-end', (region, e) => {
          this.currentRegionId = region.id
          this.currentRegion.start = region.start
          this.currentRegion.end = region.end
          // eslint-disable-next-line no-console
          console.log(region, this.currentRegion)
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
    },
    saveRegion () {
      if (![undefined, '', ' ', null].includes(this.currentRegion.text.trim())) {
        this.player.regions.list[this.currentRegionId].text = this.currentRegion.text
        this.player.regions.list[this.currentRegionId].color = 'rgba(0, 255, 0, 0.1)'
        this.player.regions.list[this.currentRegionId].element.style.backgroundColor = 'rgba(0, 255, 0, 0.1)'
      } else {
        this.player.regions.list[this.currentRegionId].text = null
        this.player.regions.list[this.currentRegionId].color = 'rgba(0, 0, 0, 0.1)'
        this.player.regions.list[this.currentRegionId].element.style.backgroundColor = 'rgba(0, 0, 0, 0.1)'
      }
    },
    deleteRegion () {
      // eslint-disable-next-line no-console
      console.log(this.currentRegionId)
      this.player.regions.list[this.currentRegionId].remove()
      this.currentRegionId = undefined
    }
  }
}
</script>
<style>
.wavesurfer-handle {
  width: 2px !important;
}

</style>
