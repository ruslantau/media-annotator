<template>
  <div>
    <a-card>
      <a-table bordered :data-source="dataSource" :columns="columns" row-key="id">
        <template slot="name" slot-scope="text, record">
          <editable-cell :text="text" :href="'http://localhost:3000/projects/' + record.id" @change="onCellChange(record.key, 'name', $event)" />
        </template>
        <template slot="progress" slot-scope="text, record">
          <a-progress :percent="countAnnotated(record.data)" />
        </template>
        <template slot="operation" slot-scope="text, record">
          <a-popconfirm
            v-if="dataSource.length"
            title="Sure to delete?"
            @confirm="() => onDelete(record.id)"
          >
            <a href="javascript:;">Delete</a>
          </a-popconfirm>
        </template>
      </a-table>
    </a-card>
    <a-card style="margin-top: 24px;">
      <media-tree-select />
    </a-card>
  </div>
</template>
<script>
const EditableCell = {
  template: `
      <div class="editable-cell">
        <div v-if="editable" class="editable-cell-input-wrapper">
          <a-input :value="value" @change="handleChange" @pressEnter="check" /><a-icon
            type="check"
            class="editable-cell-icon-check"
            @click="check"
          />
        </div>
        <div v-else class="editable-cell-text-wrapper">
          <a :href="href">{{ value || ' ' }}</a>
          <a-icon type="edit" class="editable-cell-icon" @click="edit" />
        </div>
      </div>
    `,
  props: {
    text: String,
    href: String
  },
  data () {
    return {
      value: this.text,
      editable: false
    }
  },
  methods: {
    handleChange (e) {
      const value = e.target.value
      this.value = value
    },
    check () {
      this.editable = false
      this.$emit('change', this.value)
    },
    edit () {
      this.editable = true
    }
  }
}
export default {
  name: 'ProjectsTable',
  components: {
    EditableCell
  },
  data () {
    return {
      dataSource: [],
      columns: [
        {
          title: 'Project name',
          dataIndex: 'name',
          scopedSlots: { customRender: 'name' }
        },
        {
          title: 'Annotation progress',
          dataIndex: 'progress',
          scopedSlots: { customRender: 'progress' }
        },
        {
          title: 'operation',
          dataIndex: 'operation',
          scopedSlots: { customRender: 'operation' }
        }
      ]
    }
  },
  async fetch () {
    this.dataSource = await fetch('http://localhost:8000/projects')
      .then(res => res.json())
      .catch(e => console.log(e))
  },
  mounted () {
    this.$nuxt.$on('update-projects-table', (e) => {
      this.$fetch()
    })
  },
  methods: {
    async onCellChange (key, dataIndex, value) {
      const dataSource = [...this.dataSource]
      const target = dataSource.find(item => item.key === key)

      if (target) {
        await fetch(`http://localhost:8000/projects/${target.id}`, {
          method: 'PUT',
          body: JSON.stringify({ name: value })
        })
          .then((response) => {
            if (response.ok) {
              target[dataIndex] = value
              this.dataSource = dataSource
              this.$message.success('Project name updated.')
            } else {
              this.$message.error('Project name update failed.')
            }
          })
          .catch((e) => {
            this.$message.error('Project name update failed.' + e)
          })
      }
      console.log(key, dataIndex, value)
    },
    async onDelete (id) {
      await fetch(`http://localhost:8000/projects/${id}`, { method: 'DELETE' })
        .then(res => this.$fetch())
        .catch(e => console.log(e))
    },
    countAnnotated (data) {
      const annotatedMask = data.map(function (obj, index) {
        return obj.annotations.length > 0
      })
      const annotated = annotatedMask.reduce((partialSum, a) => partialSum + a, 0)
      return Number((annotated / data.length * 100).toFixed(0))
    }
  }
}
</script>
<style>
.editable-cell {
  position: relative;
}

.editable-cell-input-wrapper,
.editable-cell-text-wrapper {
  padding-right: 24px;
}

.editable-cell-text-wrapper {
  padding: 5px 24px 5px 5px;
}

.editable-cell-icon,
.editable-cell-icon-check {
  position: absolute;
  right: 0;
  width: 20px;
  cursor: pointer;
}

.editable-cell-icon {
  line-height: 18px;
  display: none;
}

.editable-cell-icon-check {
  line-height: 28px;
}

.editable-cell:hover .editable-cell-icon {
  display: inline-block;
}

.editable-cell-icon:hover,
.editable-cell-icon-check:hover {
  color: #108ee9;
}
</style>
