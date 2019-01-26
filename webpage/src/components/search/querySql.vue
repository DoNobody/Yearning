<style lang="less">
  @import '../../styles/common.less';
  @import '../order/components/table.less';

  .tree {
    word-wrap: break-word;
    word-break: break-all;
    overflow-y: scroll;
    overflow-x: scroll;
    height: 680px;
  }
</style>

<template>
  <div>
    <Row>
      <Col span="4">
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
      </Col>
      <Col span="20" class="padding-left-10">
          <Row>
            <Card>
              <div slot="title">
                <Button type="error" icon="md-trash" @click.native="ClearForm()">清除</Button>
                <Button type="info" icon="md-brush" @click.native="beautify()">美化</Button>
                <Button v-if="formItem.selectContent" type="success" icon="ios-redo" @click.native="Search_sql()">
                  查询已选择</Button>
                <Button v-else type="success" icon="ios-redo" @click.native="Search_sql()">查询</Button>
                <Button type="primary" icon="ios-cloud-download" @click.native="exportdata()" v-if="put_info.export_data">导出查询数据</Button>
                <span v-if = "put_info.base">
                  <b>当前选择的库:</b>
                  <span>{{put_info.dbcon}} . {{put_info.base}}</span>
                  <b>延时:</b>
                  <span v-if="put_info.slave_delay > 0" style="background-color:red;">{{ put_info.slave_delay }}</span>
                  <span v-else>{{ put_info.slave_delay }}</span>
                  <b>秒</b>
                </span>
              </div>
              <Button type="primary" icon="md-add" @click.native="search_perm()" slot="extra">查询权限</Button>
              <editor v-model="formItem.textarea" @init="editorInit" @setCompletions="setCompletions" @on-select="getSelect"  value="请输入SQL"></editor>
            </Card>
          </Row>
          <Row>
            <Input type="text" icon="search" v-model="filtertablekey" placeholder="过滤表格..." v-if="allsearchdata && allsearchdata.length"></Input>
            <Table :columns="columnsName"
              :data="allsearchdata|debouncedFilterTable(filtertablekeyLazy, page, splice_length)"
              highlight-row
              ref="table"
              stripe
              no-data-text="请输入SQL"
              border
              ></Table>
            <Page :total="total" show-total show-sizer @on-change="splice_arr" @on-page-size-change="splice_len"  ref="totol"></Page>
          </Row>
      </Col>
    </Row>
  </div>
</template>
<script>
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
      setCompletions (editor, session, pos, prefix, callback) {
        let wordList = []
        wordList = this.wordList
        callback(null, wordList.map(function (word) {
          return {
            caption: word.vl,
            value: word.vl,
            meta: word.meta
          }
        }))
      },
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
              this.wordList = this.wordList_origin.concat(this.db_keyword[i.title])
              this.put_info.export_data = c.export
              return ''
            }
            for (let t of i.children) {
              if (this.matchNode(t, vl)) {
                this.put_info.base = i.title
                this.put_info.dbcon = c.title
                this.put_info.tablename = t.title
                this.put_info.export_data = c.export
                this.wordList = this.wordList_origin.concat(this.db_keyword[i.title])
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
          if (this.put_info.dbcon !== '' && this.put_info.base !== '' && this.put_info.tablename !== '') {
            axios.put(`${util.url}/search`, {'base': this.put_info.base, 'table': this.put_info.tablename, 'dbcon': this.put_info.dbcon})
            .then(res => {
              if (res.data['error']) {
                util.err_notice(res.data['error'])
              } else {
                this.columnsName = res.data['title']
                this.allsearchdata = res.data['data']
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
      editorInit: function () {
        require('brace/mode/mysql')
        require('brace/theme/xcode')
      },
      beautify () {
        axios.put(`${util.url}/sqlsyntax/beautify`, {
          'data': this.formItem.textarea
        })
          .then(res => {
            this.formItem.textarea = res.data
            this.formItem.selectContent = ''
          })
          .catch(error => {
            util.err_notice(error)
          })
      },
      splice_arr (page) {
        this.page = page
      },
      splice_len (length) {
        this.splice_length = length
      },
      ClearForm () {
        this.formItem.textarea = ''
        this.formItem.selectContent = ''
        this.columnsName = []
        this.$refs.totol.currentPage = 1
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
        if (this.put_info.dbcon && this.put_info.base && this.allsearchdata.length) {
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
      getSelect (val) {
        this.tmpGetselect = val
      },
      setSelect () {
        let tmp = this.tmpGetselect.replace(/\s+/g, ' ')
        if (tmp !== ' ' && tmp.length > 2) {
          this.formItem.selectContent = tmp
        } else {
          this.formItem.selectContent = ''
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
                let tWord = util.highlight.split('|')
                for (let i of tWord) {
                  this.wordList_origin.push({'vl': i, 'meta': '关键字'})
                }
                this.wordList = JSON.parse(JSON.stringify(this.wordList_origin))
                this.db_keyword = res.data.highlight
              })
          } else {
            this.$router.push({
              name: 'serach-perm'
            })
          }
        })
    },
    created () {
      this.debouncedFilter = util._.debounce(this.keyfilter, 500)
      this.debouncedSelect = util._.debounce(this.setSelect, 500)
      this.debouncedSearchKey = util._.debounce(() => {
        this.filtertablekeyLazy = this.filtertablekey
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
    },
    filters: {
      debouncedFilterTable: function (val, filtertablekey, page, spliceLength) {
        return util.tableSearch(val, filtertablekey).slice((page - 1) * spliceLength, page * spliceLength)
      }
    }
  }
</script>
