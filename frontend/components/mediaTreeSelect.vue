<template>
  <div>
    <div class="clearfix">
      <a-upload-dragger
        v-if="!fileList.length > 0"
        :show-upload-list="false"
        :file-list="fileList"
        :before-upload="beforeUpload"
        :directory="true"
      >
        <a-row type="flex" justify="center" align="middle" style="height: 300px;">
          <div>
            <p class="ant-upload-drag-icon">
              <a-icon type="inbox" />
            </p>
            <p class="ant-upload-text">
              Click or drag directory to this area to select files to upload
            </p>
          </div>
        </a-row>
      </a-upload-dragger>
    </div>

    <a-directory-tree
      v-if="fileList.length > 0"
      v-model="checkedKeys"
      :tree-data="filesTree"
      :selectable="false"
      checkable
    />

    <a-button
      v-if="fileList.length > 0"
      type="primary"
      :disabled="!checkedKeys.length > 0"
      :loading="uploading"
      block
      style="margin-top: 16px"
      @click="handleUpload"
    >
      {{ uploading ? 'Uploading' : 'Start Upload' }}
    </a-button>
  </div>
</template>

<script>
const path = require('path')

export default {
  name: 'MediaTreeSelect',
  layout: 'base',
  data () {
    return {
      allowedExtensions: ['.wav', '.mp3'],
      fileList: [],
      filesTree: [],
      filesIDsToUpload: [],
      checkedKeys: [],
      uploading: false
    }
  },
  watch: {
    fileList (paths) {
      const result = []
      const level = { result }
      paths.forEach((file) => {
        const path_ = file.webkitRelativePath
        path_.split('/').reduce((r, name, i, a) => {
          if (!r[name]) {
            r[name] = { result: [] }
            const extension = path.extname(name)
            const isFile = this.allowedExtensions.includes(extension)

            r.result.push({
              title: name,
              id: isFile ? file.uid : null,
              children: r[name].result,
              ext: extension,
              isLeaf: isFile
            })
          }
          return r[name]
        }, level)
      })
      this.filesTree = result
    }
  },
  methods: {
    extractChild (obj, indexes) {
      const i = indexes.shift()
      if (i === undefined) { return null }
      if (obj[i].children.length > 0) {
        return this.extractChild(obj[i].children, indexes)
      } else {
        return obj[i]
      }
    },
    beforeUpload (file) {
      if (this.allowedExtensions.includes(path.extname(file.name))) {
        this.fileList = [...this.fileList, file]
      }
    },
    handleUpload () {
      // eslint-disable-next-line
      let formData = new FormData()
      const filesIDsToUpload = []

      this.checkedKeys.forEach((key) => {
        const k = key.split('-').map(Number)
        k.shift()
        const file = this.extractChild(this.filesTree, k)
        if (file != null) {
          filesIDsToUpload.push(file.id)
        }
      })

      const metadata = { filenames: [], paths: [], sizes: [], types: [] }
      this.fileList.forEach((file) => {
        if (filesIDsToUpload.includes(file.uid)) {
          formData.append('files', file, file.name)
          metadata.filenames.push(file.name)
          metadata.sizes.push(file.size)
          metadata.types.push(file.type)
          metadata.paths.push(file.webkitRelativePath)
          // eslint-disable-next-line
          console.log(formData.getAll('files'))
        }
      })
      formData.append('metadata', JSON.stringify(metadata))
      this.uploading = true

      fetch('http://localhost:8000/uploads', {
        method: 'POST',
        body: formData
      }).then((response) => {
        response.json()
        // eslint-disable-next-line
        console.log(1, response)
        this.$nuxt.$emit('update-projects-table')
      }).then(() => {
        this.fileList = []
        this.uploading = false
        this.$message.success('upload successfully.')
        this.$nuxt.$emit('update-projects-table')
        // eslint-disable-next-line
        console.log(2)
      }).catch(() => {
        this.uploading = false
        this.$message.error('upload failed.')
        // eslint-disable-next-line
        console.log(3)
      })
    }
  }
}
</script>
