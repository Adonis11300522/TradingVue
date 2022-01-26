<template>
    <!-- Main component  -->
    <div class="trading-vue" v-bind:id="id"
         @mousedown="mousedown" @mouseleave="mouseleave"
         :style="{
            color: this.chart_props.colors.text,
            font: this.font_comp,
            width: this.width+'px',
            height: this.height+'px'}">
        <toolbar v-if="toolbar"
                 ref="toolbar"
                 v-on:custom-event="custom_event"
                 v-bind="chart_props"
                 v-bind:config="chart_config">
        </toolbar>
        <widgets v-if="controllers.length"
                 ref="widgets"
                 :map="ws" :width="width" :height="height"
                 :tv="this" :dc="data">
        </widgets>
        <button v-if="drawbutton" type="button" class="btn btn-primary" style="z-index: 11" @click="convert">Draw</button>
        <select id="linewidth" v-if="!drawbutton" @change="changeLine">
            <option value="0">select line color</option>
            <option value="1">line-width: 1px</option>
            <option value="2">line-width: 2px</option>
            <option value="3">line-width: 3px</option>
            <option value="4">line-width: 4px</option>
            <option value="5">line-width: 5px</option>
        </select>
        <select id="linecolor" v-if="!drawbutton" @change="changeColor">
            <option value="0">select line width</option>
            <option value="red">red</option>
            <option value="white">white</option>
            <option value="blue">blue</option>
            <option value="green">green</option>
            <option value="yellow">yellow</option>
        </select>
        <button v-if="!drawbutton" type="button" class="btn btn-primary" style="z-index: 11" @click="stopconvert">Stop Draw</button>
        <canvas :style="'position: fixed; z-index:' + zindex" id="drawContainer" :width="w" height="360" style="z-index: 15"></canvas>
<!--        <canvas :style="'position: fixed; z-index:' + zindex" id="myCanvas" :width="w" height="360" @mousedown="beginDrawing" @mousemove="keepDrawing" @mouseup="stopDrawing" />-->
        <chart :key="reset"
               ref="chart"
               v-bind="chart_props"
               v-bind:tv_id="id"
               v-bind:config="chart_config"
               v-on:custom-event="custom_event"
               v-on:range-changed="range_changed"
               v-on:legend-button-click="legend_button">
        </chart>
        <transition name="tvjs-drift">
            <the-tip :data="tip" v-if="tip"
                     @remove-me="tip = null"/>
        </transition>
    </div>
</template>

<script>

    import Const from './stuff/constants.js'
    import Chart from './components/Chart.vue'
    import Toolbar from './components/Toolbar.vue'
    import Widgets from './components/Widgets.vue'
    import TheTip from './components/TheTip.vue'
    import XControl from './mixins/xcontrol.js'

    export default {
        name: 'TradingVue',
        components: {
            Chart, Toolbar, Widgets, TheTip
        },
        mixins: [XControl],
        props: {
            titleTxt: {
                type: String,
                default: 'Graphic Project'
            },
            id: {
                type: String,
                default: 'trading-vue-js'
            },
            width: {
                type: Number,
                default: 800
            },
            height: {
                type: Number,
                default: 421
            },
            colorTitle: {
                type: String,
                default: '#42b883'
            },
            colorBack: {
                type: String,
                default: '#121826'
            },
            colorGrid: {
                type: String,
                default: '#2f3240'
            },
            colorText: {
                type: String,
                default: '#dedddd'
            },
            colorTextHL: {
                type: String,
                default: '#fff'
            },
            colorScale: {
                type: String,
                default: '#838383'
            },
            colorCross: {
                type: String,
                default: '#8091a0'
            },
            colorCandleUp: {
                type: String,
                default: '#23a776'
            },
            colorCandleDw: {
                type: String,
                default: '#e54150'
            },
            colorWickUp: {
                type: String,
                default: '#23a77688'
            },
            colorWickDw: {
                type: String,
                default: '#e5415088'
            },
            colorWickSm: {
                type: String,
                default: 'transparent' // deprecated
            },
            colorVolUp: {
                type: String,
                default: '#79999e42'
            },
            colorVolDw: {
                type: String,
                default: '#ef535042'
            },
            colorPanel: {
                type: String,
                default: '#565c68'
            },
            colorTbBack: {
                type: String
            },
            colorTbBorder: {
                type: String,
                default: '#8282827d'
            },
            colors: {
                type: Object
            },
            font: {
                type: String,
                default: Const.ChartConfig.FONT
            },
            toolbar: {
                type: Boolean,
                default: false
            },
            data: {
                type: Object,
                required: true
            },
            // Your overlay classes here
            overlays: {
                type: Array,
                default: function () {
                    return []
                }
            },
            // Overwrites ChartConfig values,
            // see constants.js
            chartConfig: {
                type: Object,
                default: function () {
                    return {}
                }
            },
            legendButtons: {
                type: Array,
                default: function () {
                    return []
                }
            },
            indexBased: {
                type: Boolean,
                default: false
            },
            extensions: {
                type: Array,
                default: function () {
                    return []
                }
            },
            xSettings: {
                type: Object,
                default: function () {
                    return {}
                }
            },
            skin: {
                type: String // Skin Name
            },
            timezone: {
                type: Number,
                default: 0
            }
        },
        computed: {
            // Copy a subset of TradingVue props
            chart_props() {
                let offset = this.$props.toolbar ?
                    this.chart_config.TOOLBAR : 0
                let chart_props = {
                    title_txt: this.$props.titleTxt,
                    overlays: this.$props.overlays.concat(this.mod_ovs),
                    data: this.decubed,
                    width: this.$props.width - offset,
                    height: this.$props.height,
                    font: this.font_comp,
                    buttons: this.$props.legendButtons,
                    toolbar: this.$props.toolbar,
                    ib: this.$props.indexBased || this.index_based || false,
                    colors: Object.assign({}, this.$props.colors ||
                        this.colorpack),
                    skin: this.skin_proto,
                    timezone: this.$props.timezone
                }

                this.parse_colors(chart_props.colors)
                return chart_props
            },
            chart_config() {
                return Object.assign({},
                    Const.ChartConfig,
                    this.$props.chartConfig,
                )
            },
            decubed() {
                let data = this.$props.data
                if (data.data !== undefined) {
                    // DataCube detected
                    data.init_tvjs(this)
                    return data.data
                } else {
                    return data
                }
            },
            index_based() {
                const base = this.$props.data
                if (base.chart) {
                    return base.chart.indexBased
                } else if (base.data) {
                    return base.data.chart.indexBased
                }
                return false
            },
            mod_ovs() {
                let arr = []
                for (var x of this.$props.extensions) {
                    arr.push(...Object.values(x.overlays))
                }
                return arr
            },
            font_comp() {
                return this.skin_proto && this.skin_proto.font ?
                    this.skin_proto.font : this.font
            }
        },
        data() {
            return {reset: 0,
                tip: null,
                zindex: 0,
                x: 0,
                y: 0,
                startPosition: {x: 0, y: 0},
                lineCoordinates: {x: 0, y: 0},
                isDrawStart: false,
                drawbutton:true,
                w:window.innerWidth,
                isDrawing: false,
                canvas: null,
                canvasEle: {},
                context: {},
                lineWidth: 1,
                linecolor: 'white'
            }
        },
        beforeDestroy() {
            this.custom_event({event: 'before-destroy'})
            this.ctrl_destroy()
        },
        mounted() {
            // var c = document.getElementById("myCanvas");
            // this.canvas = c.getContext('2d');
            this.canvasEle = document.getElementById('drawContainer');
            this.context = this.canvasEle.getContext('2d');
            this.canvasEle.addEventListener('mousedown', this.mouseDownListener);
            this.canvasEle.addEventListener('mousemove', this.mouseMoveListener);
            this.canvasEle.addEventListener('mouseup', this.mouseupListener);

            this.canvasEle.addEventListener('touchstart', this.mouseDownListener);
            this.canvasEle.addEventListener('touchmove', this.mouseMoveListener);
            this.canvasEle.addEventListener('touchend', this.mouseupListener);
        },
        methods: {
            changeColor(e) {
                console.log(e.target.value)
                this.linecolor = e.target.value;
            },
            changeLine(e) {
              this.lineWidth = e.target.value;
            },
            getClientOffset(event) {
                const {pageX, pageY} = event.touches ? event.touches[0] : event;
                const x = pageX - this.canvasEle.offsetLeft;
                const y = pageY - this.canvasEle.offsetTop;

                return {
                    x,
                    y
                }
            },

            drawLine() {
                this.context.beginPath();
                this.context.strokeStyle = this.linecolor;
                this.context.lineWidth = this.lineWidth;
                this.context.moveTo(this.startPosition.x, this.startPosition.y);
                this.context.lineTo(this.lineCoordinates.x, this.lineCoordinates.y);
                this.context.stroke();
            },

            mouseDownListener (event) {
                this.startPosition = this.getClientOffset(event);
                this.isDrawStart = true;
            },

            mouseMoveListener (event) {
                if(!this.isDrawStart) return;

                this.lineCoordinates = this.getClientOffset(event);
                this.clearCanvas();
                this.drawLine();
            },

            mouseupListener (event) {
                this.isDrawStart = false;
            },

            clearCanvas() {
                this.context.clearRect(0, 0, this.canvasEle.width, this.canvasEle.height);
            },

            convert() {
                this.drawbutton = false;
                this.zindex = 10;
            },
            stopconvert() {
                this.zindex = 0;
                this.drawbutton = true;

            },
            // drawLine(x1, y1, x2, y2) {
            //     let ctx = this.canvas;
            //     ctx.beginPath();
            //     ctx.strokeStyle = 'white';
            //     ctx.lineWidth = 2;
            //     ctx.moveTo(x1, y1);
            //     ctx.lineTo(x2, y2);
            //     ctx.stroke();
            //     ctx.closePath();
            // },
            // beginDrawing(e) {
            //     this.x = e.offsetX;
            //     this.y = e.offsetY;
            //     this.isDrawing = true;
            // },
            // keepDrawing(e) {
            //     if (this.isDrawing === true) {
            //         this.drawLine(this.x, this.y, e.offsetX, e.offsetY);
            //         this.x = e.offsetX;
            //         this.y = e.offsetY;
            //     }
            // },
            // stopDrawing(e) {
            //     if (this.isDrawing === true) {
            //         this.drawLine(this.x, this.y, e.offsetX, e.offsetY);
            //         this.x = 0;
            //         this.y = 0;
            //         this.isDrawing = false;
            //     }
            // },
            // TODO: reset extensions?
            resetChart(resetRange = true) {
                this.reset++
                let range = this.getRange()
                if (!resetRange && range[0] && range[1]) {
                    this.$nextTick(() => this.setRange(...range))
                }
                this.$nextTick(() => this.custom_event({
                    event: 'chart-reset', args: []
                }))
            },
            goto(t) {
                // TODO: limit goto & setRange (out of data error)
                if (this.chart_props.ib) {
                    const ti_map = this.$refs.chart.ti_map
                    t = ti_map.gt2i(t, this.$refs.chart.ohlcv)
                }
                this.$refs.chart.goto(t)
            },
            setRange(t1, t2) {
                if (this.chart_props.ib) {
                    const ti_map = this.$refs.chart.ti_map
                    const ohlcv = this.$refs.chart.ohlcv
                    t1 = ti_map.gt2i(t1, ohlcv)
                    t2 = ti_map.gt2i(t2, ohlcv)
                }
                this.$refs.chart.setRange(t1, t2)
            },
            getRange() {
                if (this.chart_props.ib) {
                    const ti_map = this.$refs.chart.ti_map
                    // Time range => index range
                    return this.$refs.chart.range
                        .map(x => ti_map.i2t(x))
                }
                return this.$refs.chart.range
            },
            getCursor() {

                let cursor = this.$refs.chart.cursor
                if (this.chart_props.ib) {
                    const ti_map = this.$refs.chart.ti_map
                    let copy = Object.assign({}, cursor)
                    copy.i = copy.t
                    copy.t = ti_map.i2t(copy.t)
                    return copy
                }
                return cursor
            },
            showTheTip(text, color = "orange") {
                this.tip = {text, color}
            },
            legend_button(event) {
                this.custom_event({
                    event: 'legend-button-click', args: [event]
                })
            },
            custom_event(d) {
                if ('args' in d) {
                    this.$emit(d.event, ...d.args)
                } else {
                    this.$emit(d.event)
                }
                let data = this.$props.data
                let ctrl = this.controllers.length !== 0
                if (ctrl) this.pre_dc(d)
                if (data.tv) {
                    // If the data object is DataCube
                    data.on_custom_event(d.event, d.args)
                }
                if (ctrl) this.post_dc(d)
            },
            range_changed(r) {
                if (this.chart_props.ib) {
                    const ti_map = this.$refs.chart.ti_map
                    r = r.map(x => ti_map.i2t(x))
                }
                this.$emit('range-changed', r)
                this.custom_event(
                    {event: 'range-changed', args: [r]}
                )
                if (this.onrange) this.onrange(r)
            },
            set_loader(dc) {
                this.onrange = r => {
                    let pf = this.chart_props.ib ? '_ms' : ''
                    let tf = this.$refs.chart['interval' + pf]
                    dc.range_changed(r, tf)
                }
            },
            parse_colors(colors) {
                for (var k in this.$props) {
                    if (k.indexOf('color') === 0 && k !== 'colors') {
                        let k2 = k.replace('color', '')
                        k2 = k2[0].toLowerCase() + k2.slice(1)
                        if (colors[k2]) continue
                        colors[k2] = this.$props[k]
                    }
                }
            },
            mousedown() {
                this.$refs.chart.activated = true
            },
            mouseleave() {
                this.$refs.chart.activated = false
            }
        }
    }
</script>
<style>
    /* Anit-boostrap tactix */
    .trading-vue *, ::after, ::before {
        box-sizing: content-box;
    }

    .trading-vue img {
        vertical-align: initial;
    }
    #myCanvas {
        color: #2f6627;
    }
    button {
        position: fixed;
        top: 10px;
        right: 100px;
    }
    #linewidth {
       position: fixed;
       top: 10px;
       right: 200px;
       z-index: 13;
    }
    #linecolor {
        position: fixed;
        top: 10px;
        right: 330px;
        z-index: 13;
    }
</style>
