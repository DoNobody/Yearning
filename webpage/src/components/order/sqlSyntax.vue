<style lang="less">
  @import '../../styles/common.less';
  @import 'components/table.less';
</style>

<template>
  <div>
    <Row>
      <Col span="6">
        <Card>
          <p slot="title">
            <Icon type="ios-redo"></Icon>
            选择数据库
          </p>
          <div class="edittable-test-con">
            <div id="showImage" class="margin-bottom-10">

              <Form ref="formItem" :model="formItem" :rules="ruleValidate" :label-width="80">
                <FormItem label="机房:" prop="computer_room">
                  <Select v-model="formItem.computer_room" @on-change="Connection_Name">
                    <Option v-for="i in datalist.computer_roomlist" :key="i" :value="i">{{i}}</Option>
                  </Select>
                </FormItem>

                <FormItem label="连接名:" prop="connection_name">
                  <Select v-model="formItem.connection_name" @on-change="DataBaseName" filterable :disabled="formItem.textarea.length !== 0" ref="connection_name">
                    <Option v-for="i in datalist.connection_name_list" :value="i.connection_name"
                            :key="i.connection_name">{{ i.connection_name }}
                    </Option>
                  </Select>
                </FormItem>

                <FormItem label="库名:" prop="basename">
                  <Select v-model="formItem.basename" filterable :disabled="formItem.textarea.length !== 0" ref="basename">
                    <Option v-for="item in datalist.basenamelist" :value="item" :key="item">{{ item }}</Option>
                  </Select>
                </FormItem>

                <FormItem label="指定审核人:" prop="assigned">
                  <Select v-model="formItem.assigned" filterable ref="assigned">
                    <Option v-for="i in datalist.assigend" :value="i" :key="i">{{i}}</Option>
                  </Select>
                </FormItem>

                <FormItem label="工单说明:" prop="text">
                  <Input v-model="formItem.text" placeholder="请输入"></Input>
                </FormItem>

                <FormItem label="是否备份">
                  <RadioGroup v-model="formItem.backup">
                    <Radio label="1" :disabled="backup_disable">是</Radio>
                    <Radio label="0">否</Radio>
                    <Radio v-if="backup_disable" label="无备份权限" disabled></Radio>
                  </RadioGroup>
                </FormItem>

                <FormItem label="延迟执行">
                  <InputNumber
                    v-model="formItem.delay"
                    :formatter="value => `${value}分钟`"
                    :parser="value => value.replace('分钟', '')"
                    :min="0">
                  </InputNumber>
                </FormItem>

              </Form>
              <Form :label-width="30">
                <FormItem>
                  <Button type="info" icon="md-brush" @click.native="beautify()">美化</Button>
                  <Button type="error" icon="md-trash" @click.native="ClearForm()" style="margin-left: 10%">清除</Button>
                </FormItem>

                <FormItem>
                  <Button type="warning" icon="md-search" @click.native="test_sql()" :disabled="formItem.textarea.length === 0">检测</Button>
                  <Button type="success" icon="ios-redo" @click.native="SubmitSQL()" style="margin-left: 10%"
                          :disabled="this.validate_sub">提交
                  </Button>
                </FormItem>
              </Form>

              <Alert style="height: 145px">
                检测表字段提示信息
                <template slot="desc">
                  <p>1.错误等级 0正常,1警告,2错误。</p>
                  <p>2.阶段状态 审核成功,Audit completed</p>
                  <p>3.错误信息 用来表示出错错误信息</p>
                  <p>4.当前检查的sql</p>
                  <p>注:只有错误等级等于0时提交按钮才会激活</p>
                </template>
              </Alert>
            </div>
          </div>
        </Card>
      </Col>
      <Col span="18" class="padding-left-10">
        <Card>
          <p slot="title">
            <Icon type="ios-crop"></Icon>
            填写sql语句
          </p>
          <editor v-model="formItem.textarea" @init="editorInit" @setCompletions="setCompletions" style="min-height: 250px !important;"></editor>
          <br>
          <br>
          <Table :columns="columnsName" :data="Testresults" highlight-row></Table>
        </Card>
      </Col>
    </Row>
  </div>
</template>
<script>
  import ICol from '../../../node_modules/iview/src/components/grid/col.vue'
  import axios from 'axios'
  import util from '../../libs/util'

  export default {
    components: {
      ICol,
      editor: require('../../libs/editor')
    },
    name: 'SQLsyntax',
    data () {
      return {
        validate_gen: true,
        formItem: {
          textarea: '',
          checkedsql: '',
          computer_room: '',
          connection_name: '',
          basename: '',
          text: '',
          backup: '0',
          assigned: '',
          delay: 0
        },
        columnsName: [
          {
            title: 'ID',
            key: 'ID',
            width: 50
          },
          {
            title: '错误等级',
            key: 'errlevel',
            width: 85
          },
          {
            title: '阶段状态',
            key: 'stagestatus'
          },
          {
            title: '错误信息',
            key: 'errormessage'
          },
          {
            title: '当前检查的sql',
            key: 'sql'
          },
          {
            title: '预计影响的SQL',
            key: 'affected_rows'
          },
          {
            title: 'SQLSHA1',
            key: 'SQLSHA1'
          }
        ],
        Testresults: [],
        item: {},
        datalist: {
          connection_name_list: [],
          basenamelist: [],
          sqllist: [],
          computer_roomlist: [],
          assigend: []
        },
        ruleValidate: {
          computer_room: [{
            required: true,
            message: '机房地址不得为空',
            trigger: 'change'
          }],
          connection_name: [{
            required: true,
            message: '连接名不得为空',
            trigger: 'change'
          }],
          basename: [{
            required: true,
            message: '数据库名不得为空',
            trigger: 'change'
          }],
          text: [{
            required: true,
            message: '说明不得为空',
            trigger: 'blur'
          }
          ],
          assigned: [{
            required: true,
            message: '审核人不得为空',
            trigger: 'change'
          }]
        },
        id: null,
        assigned: [],
        wordList: [],
        backup_disable: false
      }
    },
    methods: {
      setCompletions (editor, session, pos, prefix, callback) {
        callback(null, this.wordList.map(function (word) {
          return {
            caption: word.vl,
            value: word.vl,
            meta: word.meta
          }
        }))
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
          })
          .catch(error => {
            util.err_notice(error)
          })
      },
      Connection_Name (val) {
        // 初始化备选项
        this.datalist.basenamelist = []
        this.datalist.assigend = []
        // 初始化选择值
        this.formItem.connection_name = ''
        this.formItem.basename = ''
        this.formItem.assigned = ''
        // 清空被选中项目
        this.$refs.connection_name.setQuery(' ')
        this.$refs.basename.setQuery(' ')
        this.$refs.assigned.setQuery(' ')
        this.datalist.connection_name_list = this.item.filter(item => {
          if (item.computer_room === val) {
            return item
          }
        })
      },
      DataBaseName (index) {
        if (index) {
          this.id = this.item.filter(item => {
            if (item.connection_name === index) {
              return item
            }
          })
          axios.put(`${util.url}/workorder/basename`, {
            'id': this.id[0].id
          })
            .then(res => {
              // 初始化备选项
              this.datalist.basenamelist = res.data
              this.datalist.assigned = []
              // 初始化选择值
              this.formItem.basename = ''
              this.formItem.assigned = ''
              // 清空被选中项目
              this.$refs.basename.setQuery(' ')
              this.$refs.assigned.setQuery(' ')
              // 设置backup默认选项
              if (this.id.length > 0 && this.id[0].dbtype === 'mysql' && this.id[0].has_repl_perm) {
                this.backup_disable = false
              } else {
                this.formItem.backup = '0'
                this.backup_disable = true
              }
            })
            .catch(() => {
              util.err_notice('无法连接数据库!请检查网络')
            })
        }
        axios.put(`${util.url}/workorder/connection`, {
          'permissions_type': 'dml',
           'dmlcon': [index]
        })
          .then(res => {
            this.datalist.assigend = res.data['assigend']
          })
          .catch(error => {
            util.err_notice(error)
          })
      },
      test_sql () {
        let ddl = ['select', 'alter', 'drop', 'create']
        let dmlsql = this.formItem.textarea.replace(/(;|；)$/gi, '').replace(/\s/g, ' ').replace(/；/g, ';').split(';')
        for (let i of dmlsql) {
          for (let c of ddl) {
            i = i.replace(/(^\s*)|(\s*$)/g, '')
            if (i.toLowerCase().indexOf(c) === 0) {
              this.$Message.error('不可提交非DML语句!')
              return false
            }
          }
        }
        this.$refs['formItem'].validate((valid) => {
          if (valid) {
            if (this.formItem.textarea) {
              let tmp = this.formItem.textarea.replace(/(;|；)$/gi, '').replace(/；/g, ';')
              axios.put(`${util.url}/sqlsyntax/test`, {
                'id': this.id[0].id,
                'basename': this.formItem.basename,
                'sql': tmp
              })
                .then(res => {
                  if (res.data.status === 200) {
                    this.Testresults = res.data.result
                    let gen = 0
                    this.Testresults.forEach(vl => {
                      if (vl.errlevel !== 0) {
                        gen += 1
                      }
                    })
                    if (gen === 0) {
                      this.validate_gen = false
                      this.formItem.checkedsql = this.formItem.textarea
                    } else {
                      this.validate_gen = true
                    }
                  }
                })
                .catch(() => {
                  util.err_notice('无法连接到Inception!')
                })
            } else {
              this.$Message.error('请填写sql语句后再测试!')
            }
          }
        })
      },
      SubmitSQL () {
        this.$refs['formItem'].validate((valid) => {
          if (valid) {
            if (this.formItem.textarea) {
              if (this.formItem.textarea === this.formItem.checkedsql) {
                this.datalist.sqllist = this.formItem.textarea.replace(/(;|；)$/gi, '').replace(/\s/g, ' ').replace(/；/g, ';').split(';')
                axios.post(`${util.url}/sqlsyntax/`, {
                  'data': JSON.stringify(this.formItem),
                  'sql': JSON.stringify(this.datalist.sqllist),
                  'real_name': sessionStorage.getItem('real_name'),
                  'type': 1,
                  'id': this.id[0].id
                })
                  .then(res => {
                    this.$Notice.success({
                      title: '成功',
                      desc: res.data
                    })
                    this.ClearForm()
                  })
                  .catch(error => {
                    util.err_notice(error)
                  })
              } else {
                this.$Message.error('sql语句有变动,请重新检测')
                this.validate_gen = true
              }
            } else {
              this.$Message.error('请填写sql语句后再提交!')
            }
            this.validate_gen = true
          } else {
            this.$Message.error('表单验证失败!')
          }
        })
      },
      ClearForm () {
        this.formItem.textarea = ''
      },
      getdatabases (dmlcon = []) {
        axios.put(`${util.url}/workorder/connection`, {
          'permissions_type': 'dml',
           'dmlcon': dmlcon
        })
          .then(res => {
            this.item = res.data['connection']
            this.assigned = res.data['assigend']
            this.datalist.computer_roomlist = res.data['custom']
          })
          .catch(error => {
            util.err_notice(error)
          })
      }
    },
    computed: {
      validate_sub: function () {
        if (this.validate_gen | (this.formItem.checkedsql.length === 0) | (this.formItem.textarea !== this.formItem.checkedsql)) {
          return true
        } else {
          return false
        }
      }
    },
    mounted () {
      this.getdatabases()
      for (let i of util.highlight.split('|')) {
        this.wordList.push({'vl': i, 'meta': '关键字'})
      }
    }
  }
</script>
