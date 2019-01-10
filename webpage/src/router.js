import Index from './main.vue'

export const loginRouter = {
  path: '/login',
  name: 'login',
  meta: {
    title: 'Login - 登录'
  },
  component: resolve => {
    require(['./login.vue'], resolve)
  }
}
export const version = {
  path: '/version',
  name: 'version',
  meta: {
    title: 'version - 版本号'
  },
  component: resolve => {
    require(['./main_components/version.vue'], resolve)
  }
}
export const locking = {
  path: '/locking',
  name: 'locking',
  component: resolve => {
    require(['./main_components/locking-page.vue'], resolve)
  }
}

export const page404 = {
  path: '/*',
  name: 'error_404',
  meta: {
    title: '404-页面不存在'
  },
  component: resolve => {
    require(['./components/error/404.vue'], resolve)
  }
}

export const page401 = {
  path: '/401',
  meta: {
    title: '401-权限不足'
  },
  name: 'error_401',
  component: resolve => {
    require(['./components/error/401.vue'], resolve)
  }
}

export const page500 = {
  path: '/500',
  meta: {
    title: '500-服务端错误'
  },
  name: 'error_500',
  component: resolve => {
    require(['./components/error/500.vue'], resolve)
  }
}

/* 默认菜单权限控制:
  access:  //控制功能
    0: perform,manager,admin所有人可见
    1: manager,admin 可见
    2: admin 可见
  后端返回的permission, 对库表控制
*/
// 统一的main页面的child页面
const mainchild = [
  {
    path: 'home',
    title: '首页',
    name: 'home_index',
    component: resolve => {
      require(['./components/home/home.vue'], resolve)
    }
  },
  {
    path: 'ownspace',
    title: '个人中心',
    name: 'ownspace_index',
    component: resolve => {
      require(['./components/personalCenter/own-space.vue'], resolve)
    }
  },
  {
    path: 'queryready',
    title: '查询申请进度',
    name: 'queryready',
    component: resolve => {
      require(['./components/search/queryPerms.vue'], resolve)
    }
  },
  {
    path: 'serach-perm',
    name: 'serach-perm',
    title: 'SQL查询',
    'icon': 'ios-podium',
    component: resolve => {
      require(['./components/search/workFlow.vue'], resolve)
    }
  },
  {
    path: 'querylist',
    title: '查询审计详情',
    name: 'querylist',
    component: resolve => {
      require(['./components/audit/expend.vue'], resolve)
    }
  },
  {
    path: 'orderlist',
    title: '工单详情',
    name: 'orderlist',
    component: resolve => {
      require(['./components/order/components/myorderList.vue'], resolve)
    }
  },
  {
    path: 'myorder',
    name: 'myorder',
    title: '我的工单',
    'icon': 'person',
    component: resolve => {
      require(['./components/audit/sqlAudit.vue'], resolve)
    }
  }
]

export const appRouter = [
  {
    path: '/',
    icon: 'md-home',
    name: 'main',
    title: '首页',
    component: Index,
    redirect: '/home',
    children: [
      ...mainchild
    ]
  },
  {
    path: '/order',
    icon: 'md-folder',
    name: 'order',
    title: '工单提交',
    component: Index,
    children: [
      {
        path: 'ddledit',
        name: 'ddledit',
        title: 'DDL',
        'icon': 'md-git-merge',
        component: resolve => {
          require(['./components/order/genSql.vue'], resolve)
        }
      },
      {
        path: 'dmledit',
        name: 'dmledit',
        title: 'DML',
        'icon': 'md-code',
        component: resolve => {
          require(['./components/order/sqlSyntax.vue'], resolve)
        }
      }
    ]
  },
  {
    path: '/view',
    icon: 'md-search',
    name: 'view',
    title: '查询',
    component: Index,
    access: 1,
    children: [
      {
        path: 'querypage',
        title: 'SQL查询',
        name: 'querypage',
        icon: 'md-search',
        access: 1,
        component: resolve => {
          require(['./components/search/querySql.vue'], resolve)
        }
      },
      {
        path: 'view-dml',
        name: 'view-dml',
        title: '数据库字典',
        'icon': 'ios-book',
        access: 3,
        component: resolve => {
          require(['./components/search/databaseDic.vue'], resolve)
        }
      }

    ]
  },
  {
    path: '/audit',
    icon: 'md-open',
    name: 'audit',
    title: '审核',
    component: Index,
    access: 2,
    children: [
      {
        path: 'audit-order',
        name: 'audit-audit',
        title: '工单',
        'icon': 'md-create',
        access: 2,
        component: resolve => {
          require(['./components/audit/sqlAudit.vue'], resolve)
        }
      },
      {
        path: 'query-audit',
        name: 'query-audit',
        title: '查询',
        'icon': 'logo-rss',
        access: 2,
        component: resolve => {
          require(['./components/audit/queryAudit.vue'], resolve)
        }
      },
      {
        path: 'audit-permissions',
        name: 'audit-permissions',
        title: '权限',
        'icon': 'md-share',
        access: 2,
        component: resolve => {
          require(['./components/audit/permissions.vue'], resolve)
        }
      }
    ]
  },
  {
    path: '/record',
    icon: 'md-pie',
    name: 'record',
    title: '记录',
    component: Index,
    access: 3,
    children: [
      {
        path: 'query-review',
        name: 'query-review',
        title: '查询审计',
        'icon': 'md-pulse',
        access: 3,
        component: resolve => {
          require(['./components/assistantManger/queryRecord.vue'], resolve)
        }
      },
      {
        path: 'audit-record',
        name: 'audit-record',
        title: '工单记录',
        'icon': 'md-list',
        access: 3,
        component: resolve => {
          require(['./components/assistantManger/record.vue'], resolve)
        }
      }
    ]
  },
  {
    path: '/management',
    icon: 'logo-buffer',
    name: 'management',
    title: '管理',
    access: 2,
    component: Index,
    children: [
      {
        path: 'management-user',
        name: 'management-user',
        title: '用户',
        'icon': 'md-people',
        access: 2,
        component: resolve => {
          require(['./components/management/userInfo.vue'], resolve)
        }
      },
      {
        path: 'management-database',
        name: 'management-database',
        title: '数据库',
        'icon': 'md-medal',
        access: 3,
        component: resolve => {
          require(['./components/management/databaseManager.vue'], resolve)
        }
      },
      {
        path: 'setting',
        name: 'setting',
        title: '设置',
        access: 3,
        'icon': 'md-settings',
        component: resolve => {
          require(['./components/management/setting.vue'], resolve)
        }
      },
      {
        path: 'auth-group',
        name: 'auth-group',
        title: '权限组',
        'icon': 'ios-switch',
        access: 3,
        component: resolve => {
          require(['./components/management/authGroup.vue'], resolve)
        }
      }
    ]
  }
]

export const MainRoute = [
  loginRouter,
  locking,
  ...appRouter,
  version,
  page404,
  page401,
  page500
]
