<style lang="less">
  @import '../../styles/common.less';
  @import '../order/components/table.less';
</style>
<template>
  <div>
    <Row>
      <Card>
        <p slot="title">
          <Icon type="md-person"></Icon>
          查询审计
        </p>
        <Input type="text" icon="search" v-model="searchkey" placeholder="过滤表格当前页..." slot="extra"></Input>
        <Row>
          <Col span="24">
            <Table border :columns="columns" :data="table_data" stripe size="small"></Table>
          </Col>
        </Row>
        <br>
        <Page :total="page_number" show-elevator @on-change="currentpage" :page-size="20"></Page>
      </Card>
    </Row>
  </div>
</template>
<script>
  import axios from 'axios'
  import util from '../../libs/util'

  export default {
    name: 'put',
    data () {
      return {
        columns: [
          {
            title: '工单编号:',
            key: 'work_id',
            sortable: true
          },
          {
            title: '查询人',
            key: 'username'
          },
          {
            title: '查询人姓名',
            key: 'real_name'
          },
          {
            title: '工单说明',
            key: 'instructions'
          },
          {
            title: '提交时间:',
            key: 'date',
            sortable: true
          },
          {
            title: '操作',
            key: 'action',
            align: 'center',
            render: (h, params) => {
              return h('div', [
                h('Button', {
                  props: {
                    size: 'small',
                    type: 'text'
                  },
                  on: {
                    click: () => {
                      this.$router.push({
                        name: 'querylist',
                        query: {workid: params.row.work_id, user: params.row.username}
                      })
                    }
                  }
                }, '详细信息')
              ])
            }
          }
        ],
        page_number: 1,
        computer_room: util.computer_room,
        table_data: [],
        table_data_origin: [],
        searchkey: ''
      }
    },
    methods: {
      currentpage (vl = 1) {
        axios.get(`${util.url}/query_worklf?page=${vl}`)
          .then(res => {
            this.table_data_origin = res.data.data
            this.table_data = JSON.parse(JSON.stringify(this.table_data_origin))
            this.page_number = res.data.page
          })
          .catch(error => {
            util.err_notice(error)
          })
      }
    },
    watch: {
      searchkey: function () {
        this.lazytable_data()
      }
    },
    mounted () {
      this.currentpage()
    },
    created () {
      this.lazytable_data = util._.debounce(() => {
        this.table_data = util.tableSearch(this.table_data_origin, this.searchkey)
      }, 500)
    }
  }
</script>
<!-- remove delete request -->
