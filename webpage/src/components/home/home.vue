<style lang="less">
  @import "./home.less";
  @import "../../styles/common.less";

  .fuc li {
    margin-top: 2%;
    margin-left: 15%;
  }

  .fuc h4 {
    margin-top: 2%;
    margin-left: 10%;
  }
  
</style>
<template>
  <div class="home-main">
    <Row>
      <Col span="10" class-name="padding-left-5">
        <Row class="margin-top-10">
          <Row>
            <Card>
              <Row type="flex" class="user-infor">
                <Col span="8">
                  <Row class-name="made-child-con-middle" type="flex" align="middle">
                    <img class="avator-img" src="../../assets/avatar.png"/>
                  </Row>
                </Col>
                <Col span="16" style="padding-left:6px;">
                  <Row class-name="made-child-con-middle" type="flex" align="middle">
                    <div>
                      <b class="card-user-infor-name">{{username}}</b>
                      <p>Go confidently in the direction.</p>
                    </div>
                  </Row>
                </Col>
              </Row>
              <div class="line-gray"></div>
              <Row class="margin-top-8">
                <Col span="8">
                  <p class="notwrap">登陆时间:</p>
                </Col>
                <Col span="16" class="padding-left-8">{{time}}</Col>
              </Row>
            </Card>
          </Row>
          <Row>
            <Card>
              <p slot="title" class="card-title">
              <Icon type="android-map"></Icon>
                公告栏
              </p>
              <div class="data-sourcefunc-row">
                <H2>欢迎使用SQL 审核平台</H2>
                <br>
                <div class="fuc">
                  <H3>使用说明:</H3>
                  <H4 v-for="i in board.guide" :key="i">{{i}}</H4>
                </div>
              </div>
            </Card>
          </Row>
          <Row>
            <Card>
              <p slot="title" class="card-title">
              <Icon type="md-checkbox-outline"></Icon>
                待办事项
              </p>
              <a type="text" slot="extra" @click.prevent="addNewToDoItem">
                <Icon type="md-add"></Icon>
              </a>
              <Modal v-model="showAddNewTodo" title="添加新的待办事项" @on-ok="addNew" @on-cancel="cancelAdd">
                <Row type="flex" justify="center">
                  <Input v-model="newToDoItemValue" icon="compose" placeholder="请输入..." style="width: 300px"/>
                </Row>
              </Modal>
              <div class="to-do-list-con">
                <div v-for="(item, index) in toDoList" :key="index" class="to-do-item">
                  <to-do-list-item :content="item.title" :todoitem="false" @deltodo="deltodo"></to-do-list-item>
                </div>
              </div>
            </Card>
          </Row>
        </Row>
      </Col>
      <Col span="14">
        <Row class="margin-top-10">
          <Card>
            <ownspace></ownspace>
          </Card>
        </Row>
      </Col>
    </Row>
  </div>
</template>

<script>
  import axios from 'axios'
  //
  import util from '../../libs/util'
  import dataSourcePie from './components/dataSourcePie.vue'
  import inforCard from './components/inforCard.vue'
  import toDoListItem from './components/toDoListItem.vue'
  import ownspace from '../personalCenter/own-space.vue'

  export default {
    components: {
      dataSourcePie,
      inforCard,
      toDoListItem,
      ownspace
    },
    data () {
      return {
        toDoList: [{
          title: ''
        }],
        count: {
          createUser: 0,
          order: 0,
          link: 0,
          dic: 0
        },
        showAddNewTodo: false,
        newToDoItemValue: '',
        time: '',
        username: sessionStorage.getItem('user'),
        board: {
          'title': ['1.DDL语句生成', '2.数据库字典生成及查看', '3.SQL语句审核及回滚', '4.工单流程化', '5.可视化数据查询', '6.细粒度的权限划分'],
          'guide': [
              '1.点击首页右侧"权限申请", 进行对应的数据库组权限的申请，然后通知DBA进行审核。',
              '2.提交工单时，自动审核错误等级全部为0时，才能交由业务leader进行审批执行。',
              '3.使用查询时，请先在查询页面右上角点击"查看查询权限"，并进行查询权限申请，然后通知业务leader进行审核。'
            ]
        }
      }
    },
    methods: {
      addNewToDoItem () {
        this.showAddNewTodo = true
      },
      formatDate () {
        let date = new Date()
        let year = date.getFullYear()
        let month = date.getMonth() + 1
        let day = date.getDate()
        let hour = date.getHours()
        let minute = date.getMinutes()
        let second = date.getSeconds()
        this.time = year + '/' + month + '/' + day + '  ' + hour + ':' + minute + ':' + second
      },
      addNew () {
        if (this.newToDoItemValue.length !== 0) {
          axios.post(`${util.url}/homedata/todolist/`, {
            'todo': this.newToDoItemValue
          })
            .then(() => {
              let vm = this
              this.toDoList.unshift({
                title: this.newToDoItemValue
              })
              setTimeout(function () {
                vm.newToDoItemValue = ''
              }, 200)
              this.showAddNewTodo = false
            })
            .catch(error => {
              util.err_notice(error)
            })
        } else {
          this.$Message.error('请输入待办事项内容')
        }
      },
      cancelAdd () {
        this.showAddNewTodo = false
        this.newToDoItemValue = ''
      },
      deltodo (val) {
        axios.put(`${util.url}/homedata/deltodo`, {
          'todo': val
        })
          .then(() => {
            this.gettodo()
          })
          .catch(error => {
            util.err_notice(error)
          })
      },
      gettodo () {
        axios.put(`${util.url}/homedata/todolist`)
          .then(res => {
            this.toDoList = res.data
          })
          .catch(error => {
            util.err_notice(error)
          })
      }
    },
    mounted () {
      axios.get(`${util.url}/homedata/infocard`)
        .then(res => {
          this.count.dic = res.data[0]
          this.count.createUser = res.data[1]
          this.count.order = res.data[2]
          this.count.link = res.data[3]
        })
        .catch(error => {
          util.err_notice(error)
        })
      this.gettodo()
      this.formatDate()
    }
  }
</script>
