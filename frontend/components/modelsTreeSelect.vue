<template>
  <div>
    <a-tree-select
      v-model="modelName"
      style="width: auto; min-width: 200px;"
      :dropdown-style="{ maxHeight: '400px', overflow: 'auto' }"
      :tree-data="treeData"
      :disabled="isAnnotating"
      placeholder="Select model"
    />
    <a-button icon="coffee" :disabled="isDisabled" :loading="isAnnotating" @click="runModel">
      Run auto annotation
    </a-button>
  </div>
</template>

<script>
// eslint-disable-next-line no-unused-vars
export default {
  name: 'ModelsTreeSelect',
  props: {
    inputFileName: { type: String }
  },
  data () {
    return {
      isDisabled: true,
      isAnnotating: false,
      // inputFileName: 'result_wav.wav',
      modelName: null,
      treeData: [],
      annotations: []
    }
  },
  async fetch () {
    this.treeData = await fetch('http://localhost:8000/models')
      .then(res => res.json())
  },
  watch: {
    modelName () {
      this.isDisabled = this.modelName == null
    }
  },
  methods: {
    async runModel () {
      this.isAnnotating = true
      console.log(this.inputFileName, this.modelName)
      this.annotations = await fetch(`http://localhost:8000/annotate?input_file_path=${this.inputFileName}&model_dir_name=${this.modelName}`)
        .then((res) => {
          this.isAnnotating = false
          return res.json()
        })
        .catch(() => {
          this.isAnnotating = false
        })
      this.$nuxt.$emit('media-update-annotations', this.annotations)
    }
  }
}
</script>
