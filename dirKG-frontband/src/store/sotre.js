import {defineStore} from 'pinia'

export const graph = defineStore({
    id: 'graph',
    state:()  => {
        return {
            nodes: [],
            links: [],
            selectedNode: null,
        }
    },
    getters: {
        selectedNode: (state) => {
            return state.selectedNode
        },
        nodes: (state) => {
            return state.nodes
        },
        links: (state) => {
            return state.links
        }
    },
    actions: {
        setSelectedNode: (node) => {
            state.selectedNode = node
        }
    }})