<style lang="less">
  @import '../../styles/common.less';
  @import '../order/components/table.less';

  .tree {
    word-wrap: break-word;
    word-break: break-all;
    overflow-y: scroll;
    overflow-x: scroll;
    height: 766px;
  }
  .demo-split{
      height: 800px;
      border: 1px solid #dcdee2;
  }
  .demo-split-pane{
      height: 100%;
      padding: 0;
  }
  .demo-split-pane.no-padding{
      height: 100%;
      padding: 0;
  }
  .ivu-card-head{
    padding-bottom: 8px !important;
    padding-top: 8px !important;
  }
  .ivu-card-body{
    height: 100% !important;
    padding: 0 !important;
    padding-bottom: 44px !important;
  }
  .ivu-card-body-box{
    height: 100%;
  }
  .ivu-card-bordered{
    height: 100%;
  }
  .ivu-page {
    padding-left: 2%;
  }
</style>

<template>
  <div class="demo-split">
    <Split v-model="split1" mode="horizontal" @on-move-end="splitresize"> 
      <div slot="left" class="demo-split-pane">
        <Card>
          <div>
            <Icon type="ios-search"></Icon>
            <input type="text" placeholder="选择数据" class="ivu-input" style="width:90%" v-model="searchkey" value="searchkey"/>
          </div>
          <div class="edittable-test-con">
            <div id="showImage" class="margin-bottom-10">
              <div class="tree">
                <Tree :data="data1" @on-select-change="Getbasename" @on-toggle-expand="choseName"
                      @empty-text="数据加载中"></Tree>
              </div>
            </div>
          </div>
        </Card>
      </div>
      <div slot="right" class="demo-split-pane no-padding">
        <Split v-model="split2" mode="vertical" @on-move-end="splitresize" min="200px">
          <div slot="top" class="ivu-card-body-box" > 
              <Card>
                <div slot="title">
                  <Button v-if="formItem.selectContent" type="success" icon="ios-redo" @click.native="Search_sql()">
                    查询已选择</Button>
                  <Button v-else type="success" icon="ios-redo" @click.native="Search_sql()">查询</Button>
                  <Button type="info" icon="md-brush" @click.native="beautify()">美化</Button>
                  <Button type="primary" icon="ios-cloud-download" @click.native="exportdata()" ghost>导出查询数据</Button>
                  <span v-if = "put_info.base">
                    <b>当前选择的库:</b>
                    <span>{{put_info.dbcon}} . {{put_info.base}}</span>
                    <b>延时:</b>
                    <span v-if="put_info.slave_delay > 0" style="background-color:red;">{{ put_info.slave_delay }}</span>
                    <span v-else>{{ put_info.slave_delay }}</span>
                    <b>秒</b>
                  </span>
                </div>
                <Button type="primary" icon="md-add" @click.native="search_perm()" slot="extra">查看查询权限</Button>
                <editor  @input="onEditorInput" @on-select="onEditorSelect" ref="myeditor"></editor>
              </Card>
          </div>
          <div slot="bottom">
            <Row>
              <Col span="4">
                <Button type="warning" @click.native="history_sql()" v-if = "put_info.base">当前连接 历史查询记录</Button>
              </Col>
              <Col span="20">
                <Input type="text" icon="search" v-model="filtertablekey" placeholder="过滤表格..." v-if = "allsearchdata && allsearchdata.length"></Input>
              </Col>
            </Row>
            <Row>
              <Table :columns="columnsName"
                :data="allsearchdata_filtered.slice((page - 1) * splice_length, page * splice_length)"
                highlight-row
                ref="table"
                no-data-text="请输入SQL"
                border
                ></Table>
              <Page :total="total" show-total show-sizer @on-change="splice_arr" @on-page-size-change="splice_len"  ref="pager"></Page>
            </Row>
          </div>
        </Split>
      </div>
    </Split>
  </div>
</template>
<script>
  import { format } from 'sql-formatter'
  import flow from './workFlow'
  import ICol from '../../../node_modules/iview/src/components/grid/col.vue'
  import axios from 'axios'
  import util from '../../libs/util'
  import Csv from '../../../node_modules/iview/src/utils/csv'
  import ExportCsv from '../../../node_modules/iview/src/components/table/export-csv'

  const exportcsv = function exportCsv (params) {
    if (params.filename) {
      if (params.filename.indexOf('.csv') === -1) {
        params.filename += '.csv'
      }
    } else {
      params.filename = 'table.csv'
    }

    let columns = []
    let datas = []
    if (params.columns && params.data) {
      columns = params.columns
      datas = params.data
    } else {
      columns = this.columns
      if (!('original' in params)) params.original = true
      datas = params.original ? this.data : this.rebuildData
    }

    let noHeader = false
    if ('noHeader' in params) noHeader = params.noHeader
    const data = Csv(columns, datas, params, noHeader)
    if (params.callback) params.callback(data)
    else ExportCsv.download(params.filename, data)
  }
  export default {
    components: {
      ICol,
      flow,
      editor: require('../../libs/editor')
    },
    name: 'SearchSQL',
    data () {
      return {
        split1: 0.2,
        split2: 0.3,
        data1: [],
        validate_gen: true,
        formItem: {
          textarea: '',
          selectContent: ''
        },
        tmpGetselect: '',
        columnsName: [],
        ruleValidate: {
          basename: [{
            required: true,
            message: '数据库名不得为空',
            trigger: 'change'
          }]
        },
        id: null,
        total: 0,
        allsearchdata: [],
        allsearchdata_filtered: [],
        put_info: {
          base: '',
          tablename: '',
          dbcon: '',
          export_data: false,
          slave_delay: 0
        },
        wordList: [],
        wordList_origin: [],
        db_keyword: {},
        searchkey: '',
        splice_length: 10,
        page: 1,
        filtertablekey: '',
        filtertablekeyLazy: ''
      }
    },
    methods: {
      matchNode (node, vl) {
        return (node.title === vl.title && node.nodeKey === vl.nodeKey)
      },
      choseName (vl) {
        this.put_info.base = ''
        this.put_info.dbcon = ''
        this.put_info.tablename = ''
        for (let c of this.data1) {
          if (this.matchNode(c, vl)) {
            this.put_info.dbcon = c.title
            this.put_info.export_data = c.export
            return ''
          }
          for (let i of c.children) {
            if (this.matchNode(i, vl)) {
              this.put_info.dbcon = c.title
              this.put_info.base = i.title
              // 设置自动补全字段名
              this.wordList = this.db_keyword[c.title][i.title]
              this.setAutoCompleWord()
              this.put_info.export_data = c.export
              return ''
            }
            for (let t of i.children) {
              if (this.matchNode(t, vl)) {
                this.put_info.base = i.title
                this.put_info.dbcon = c.title
                this.put_info.tablename = t.title
                this.put_info.export_data = c.export
                // 设置自动补全字段名
                this.wordList = this.db_keyword[c.title][i.title]
                this.setAutoCompleWord()
                return ''
              }
            }
          }
        }
      },
      GetSlaveDelay () {
        axios.put(`${util.url}/search`, {'base': this.put_info.base, 'table': this.put_info.tablename, 'dbcon': this.put_info.dbcon, 'delaytime': 1})
            .then(res => {
              if (res.data['error']) {
                util.err_notice('获取延时信息失败:' + res.data['error'])
              } else {
                if (res.data['len'] >= 1) {
                  this.put_info.slave_delay = res.data['data'][0]['Seconds_Behind_Master']
                } else {
                  this.put_info.slave_delay = 0
                }
              }
            })
      },
      Getbasename (vl) {
        if (vl.length !== 0) {
          this.choseName(vl[0])
          this.ClearForm()
          if (this.put_info.dbcon !== '' && this.put_info.base !== '' && this.put_info.tablename !== '') {
            axios.put(`${util.url}/search`, {'base': this.put_info.base, 'table': this.put_info.tablename, 'dbcon': this.put_info.dbcon})
            .then(res => {
              if (res.data['error']) {
                util.err_notice(res.data['error'])
              } else {
                this.columnsName = res.data['title']
                this.allsearchdata = res.data['data']
                this.allsearchdata_filtered = JSON.parse(JSON.stringify(this.allsearchdata))
                this.total = res.data['len']
              }
            })
          } else {
            this.columnsName = []
            this.allsearchdata = []
            this.total = 0
          }
        }
      },
      beautify () {
        this.formItem.textarea = format(this.formItem.textarea)
        this.formItem.selectContent = ''
        this.$refs.myeditor.setValue(this.formItem.textarea)
      },
      splice_arr (page) {
        this.page = page
      },
      splice_len (length) {
        this.splice_length = length
      },
      ClearForm () {
        this.$refs.pager.currentPage = 1
        this.total = 0
        this.page = 1
      },
      Search_sql () {
        if (this.put_info.dbcon && this.put_info.base) {
          let address = {
              'dbcon': this.put_info.dbcon,
              'basename': this.put_info.base
            }
          this.$Spin.show({
            render: (h) => {
              return h('div', [
                h('Icon', {
                  props: {
                    size: 30,
                    type: 'ios-loading'
                  },
                  style: {
                    animation: 'ani-demo-spin 1s linear infinite'
                  }
                }),
                h('div', '正在查询,请稍后........')
              ])
            }
          })
          this.GetSlaveDelay()
          this.ClearForm()
          axios.post(`${util.url}/search`, {
            'sql': this.formItem.selectContent.length > 2 ? this.formItem.selectContent : this.formItem.textarea,
            'address': JSON.stringify(address)
          }).then(res => {
              if (!res.data['data']) {
                util.err_notice(res.data)
              } else {
                this.allsearchdata = res.data['data']
                this.allsearchdata_filtered = JSON.parse(JSON.stringify(this.allsearchdata))
                let dataFirst = this.allsearchdata[0]
                let dataWidth = {}
                for (let item in dataFirst) {
                  if ((dataFirst[item] + '').length > 30) {
                    dataWidth[item] = 260
                  }
                }
                this.columnsName = res.data['title'].map((item, index) => {
                  if (index === 0) {
                      item['fixed'] = 'left'
                  }
                  item['minWidth'] = 80
                  if (dataWidth[item.key]) {
                    item['width'] = dataWidth[item.key]
                  }
                  return item
                })
                this.total = res.data['len']
                this.filtertablekey = ''
                this.splice_arr(1)
              }
              this.$Spin.hide()
            }).catch(error => {
              util.err_notice(error)
              this.$Spin.hide()
            })
        } else {
          util.err_notice('请选择 数据库!')
        }
      },
      exportdata () {
        if (!this.put_info.export_data) {
            util.err_notice('无数据导出权限，点击"右侧查看权限"进行权限添加')
        } else if (this.put_info.dbcon && this.put_info.base && this.allsearchdata.length) {
          exportcsv({
            filename: this.put_info.dbcon + '-' + this.put_info.base + '-' + this.put_info.tablename + '-' + (new Date()).valueOf(),
            original: false,
            data: this.allsearchdata,
            columns: this.columnsName
          })
        } else {
          util.err_notice('请先执行 查询 数据源')
        }
      },
      search_perm () {
        this.$router.push({
          name: 'queryready'
        })
      },
      keyfilter () {
        if (this.searchkey.length !== 0) {
          let tdata = JSON.parse(JSON.stringify(this.data2))
          this.data1 = []
          for (let node of tdata) {
            let tnode = util.filternode(node, this.searchkey)
            tnode && this.data1.push(tnode)
          }
        } else {
          this.data1 = JSON.parse(JSON.stringify(this.data2))
        }
      },
      onEditorSelect (val) {
        this.tmpGetselect = val
      },
      onEditorInput (val) {
        this.formItem.textarea = val
        localStorage.setItem('querySql', this.formItem.textarea)
      },
      setAutoCompleWord () {
        this.$refs.myeditor.setHintOptions(this.wordList)
      },
      setSelect () {
        let tmp = this.tmpGetselect.replace(/\s+/g, ' ')
        if (tmp !== ' ' && tmp.length > 2) {
          this.formItem.selectContent = tmp
        } else {
          this.formItem.selectContent = ''
        }
      },
      history_sql () {
        axios.post(`${util.url}/query_history`, {
            'dbcon': this.put_info.dbcon
          }).then(res => {
              if (!res.data['data']) {
                util.err_notice(res.data['error'])
              } else {
                this.allsearchdata = res.data['data']
                this.allsearchdata_filtered = JSON.parse(JSON.stringify(this.allsearchdata))
                let dataFirst = this.allsearchdata[0]
                let dataWidth = {}
                for (let item in dataFirst) {
                  if ((dataFirst[item] + '').length > 30) {
                    dataWidth[item] = 260
                  }
                }
                this.columnsName = [{'title': '查询语句', 'key': 'statements'},
                                    {'title': '查询时间', 'key': 'updatetime'}]
                this.filtertablekey = ''
                this.total = this.allsearchdata.length
                this.splice_arr(1)
              }
            }).catch(error => {
              util.err_notice(error)
            })
      },
      splitresize () {
        if (this.split2 <= 0.2) {
          this.split2 = 0.2
        } else if (this.split2 >= 0.8) {
          this.split2 = 0.8
        }
        if (this.split1 <= 0.2) {
          this.split1 = 0.2
        } else if (this.split1 >= 0.5) {
          this.split1 = 0.5
        }
      }
    },
    mounted () {
      axios.put(`${util.url}/query_worklf`, {'mode': 'status'})
        .then(res => {
          if (res.data === 2) {
            this.$router.push({
              name: 'queryready'
            })
          } else if (res.data === 1) {
            axios.put(`${util.url}/query_worklf`, {'mode': 'info'})
              .then(res => {
                this.data1 = JSON.parse(res.data['info'])
                this.data2 = JSON.parse(res.data['info'])
                this.db_keyword = res.data.highlight
                let errorList = res.data['error_list']
                for (let i of errorList) {
                  this.$Notice.error({
                    title: '获取数据库信息错误',
                    desc: i
                  })
                }
              })
          } else {
            this.$router.push({
              name: 'serach-perm'
            })
          }
        })
      this.formItem.textarea = localStorage.getItem('querySql') || ''
      this.$refs.myeditor.setValue(this.formItem.textarea)
    },
    created () {
      this.debouncedFilter = util._.debounce(this.keyfilter, 500)
      this.debouncedSelect = util._.debounce(this.setSelect, 500)
      this.debouncedSearchKey = util._.debounce(() => {
        this.allsearchdata_filtered = util.tableSearch(this.allsearchdata, this.filtertablekey)
        this.total = this.allsearchdata_filtered.length
      }, 500)
    },
    watch: {
      searchkey: function (newkey, oldkey) {
        this.debouncedFilter()
      },
      tmpGetselect: function (newselect, oldselect) {
        this.debouncedSelect()
      },
      filtertablekey: function () {
        this.debouncedSearchKey()
      }
    }
  }
</script>
