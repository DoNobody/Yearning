<template>
    <textarea ref='mycode'></textarea>
</template>

<script>
// 核心样式
import 'codemirror/theme/idea.css';
import 'codemirror/lib/codemirror.css';
import 'codemirror/addon/hint/show-hint.css';

const CodeMirror = require('codemirror');
require('codemirror/mode/sql/sql.js');
require('codemirror/addon/selection/active-line.js');
require('codemirror/addon/edit/matchbrackets.js');
require('codemirror/addon/hint/show-hint.js');
require('codemirror/addon/display/autorefresh.js');
require('codemirror/addon/display/placeholder.js');
require('./sql-hint.js')

export default {
  props: {
    value: {
      type: String,
      default: ''
    },
    autofocus: {
      type: Boolean,
      default: true
    },
    readOnly: {
      type: [Boolean, String],
      default: false
    }
  },
  data () {
    return {
      editorText: null,
      sqlText: '',
      selectText: ''
    }
  },
  mounted () {
    this.init()
    this.setSize()
  },
  methods: {
    init () {
      this.editorText = CodeMirror.fromTextArea(this.$refs.mycode, {
        mode: 'text/x-sparksql',
        theme: 'idea',
        lineNumbers: true,
        lineWrapping: true,
        line: true,
        styleActiveLine: true,
        showCursorWhenSelecting: true,
        autofocus: this.autofocus,
        readOnly: this.readOnly,
        dragDrop: true,
        // 括号配对
        matchBrackets: true,
        autoCloseBrackets: true,
        // 自动补全
        extraKeys: { 'Tab': 'autocomplete' }, // 自定义快捷键
        hintOptions: {
          completeSingle: false,
          // 自定义提示选项
          tables: {}
        },
        placeholder: '\n\n\n请输入SQL\n点击左侧表名,查看表信息\n支持自动补全表名和字段名'
      })
      this.editorEvents()
    },
    setValue (sqls) {
      this.editorText.setValue(sqls || this.value);
    },
    setSize () {
      this.editorText.setSize('auto', '100%');
    },
    setHintOptions (tables) {
      this.editorText.options.hintOptions.tables = tables
    },
    editorEvents () {
      // 设置代码提示
      this.editorText.on('keyup', (cm, event) => {
        if (event.keyCode >= 65 && event.keyCode <= 90) {
          cm.showHint();
        }
        if (!cm.state.completionActive && ((event.keyCode >= 65 && event.keyCode <= 90) || event.keyCode === 52 || event.keyCode === 219 || event.keyCode === 190)) {
          CodeMirror.commands.autocomplete(cm, null, {completeSingle: false});
        }
      })

      // 代码输入的双向绑定
      this.editorText.on('change', (editor) => {
        // 这里要用多一个载体去获取值,不然会重复赋值卡顿
        this.sqlText = editor.getValue()
        if (this.$emit) {
          this.$emit('input', this.sqlText)
        }
      })

      // 双向绑定 选择
       this.editorText.on('cursorActivity', (editor) => {
        // 这里要用多一个载体去获取值,不然会重复赋值卡顿
        this.selectText = editor.getSelection()
        if (this.$emit) {
          this.$emit('on-select', this.selectText)
        }
      })
    }
  }
}
</script>
