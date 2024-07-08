import {createRouter, createWebHistory} from 'vue-router'
import Graph from '../components/Graph.vue'


const router = createRouter({
    history: createWebHistory(),
    routes: [
        {path:'/',
         component: Graph
        }
    ]
}) 

//全局前置路由守卫
router.beforeEach( (to,from,next) => {
    //to 是目标地包装对象  .path属性可以获取地址
    //from 是来源地包装对象 .path属性可以获取地址
    //next是方法，不调用默认拦截！ next() 放行,直接到达目标组件
    //next('/地址')可以转发到其他地址,到达目标组件前会再次经过前置路由守卫
    console.log(to.path,from.path,next)
    console.log('全局前置路由守卫')
    next()
} )

//全局后置路由守卫
router.afterEach((to, from) => {
    console.log('全局后置路由守卫')
    console.log(`Navigate from ${from.path} to ${to.path}`);
});


export default router