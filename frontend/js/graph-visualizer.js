/**
 * 图谱可视化 - 使用 Cytoscape.js 渲染人物关系图
 */

class GraphVisualizer {
    constructor(containerId) {
        this.containerId = containerId;
        this.cy = null;
    }

    /**
     * 初始化图谱
     * @param {Object} graphData - 图谱数据 {nodes, edges}
     */
    initialize(graphData) {
        const container = document.getElementById(this.containerId);

        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        // 转换数据格式为 Cytoscape 格式
        const elements = this.convertToElements(graphData);

        // 创建 Cytoscape 实例
        this.cy = cytoscape({
            container: container,
            elements: elements,
            style: this.getStyle(),
            layout: {
                name: 'cose',
                idealEdgeLength: 100,
                nodeOverlap: 20,
                refresh: 20,
                fit: true,
                padding: 30,
                randomize: false,
                componentSpacing: 100,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
            },
            wheelSensitivity: 0.2
        });

        // 添加交互事件
        this.addInteractions();
    }

    /**
     * 转换数据格式
     * @param {Object} graphData - 原始图谱数据
     * @returns {Array} Cytoscape 元素数组
     */
    convertToElements(graphData) {
        const elements = [];

        // 添加节点
        graphData.nodes.forEach(node => {
            elements.push({
                data: {
                    id: node.id,
                    label: node.label,
                    importance: node.importance || 0,
                    type: node.type || 'supporting'
                }
            });
        });

        // 添加边
        graphData.edges.forEach(edge => {
            elements.push({
                data: {
                    id: edge.id,
                    source: edge.source,
                    target: edge.target,
                    label: edge.label || '',
                    strength: edge.strength || 1
                }
            });
        });

        return elements;
    }

    /**
     * 获取样式配置
     * @returns {Array} Cytoscape 样式数组
     */
    getStyle() {
        return [
            // 节点样式
            {
                selector: 'node',
                style: {
                    'background-color': '#4a90e2',
                    'label': 'data(label)',
                    'width': 'mapData(importance, 0, 1, 30, 80)',
                    'height': 'mapData(importance, 0, 1, 30, 80)',
                    'font-size': '14px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'color': '#2c3e50',
                    'text-outline-color': '#fff',
                    'text-outline-width': 2,
                    'overlay-padding': '6px',
                    'z-index': 10
                }
            },
            // 主要人物样式
            {
                selector: 'node[type = "main"]',
                style: {
                    'background-color': '#e74c3c',
                    'width': 'mapData(importance, 0, 1, 50, 100)',
                    'height': 'mapData(importance, 0, 1, 50, 100)',
                    'font-size': '16px',
                    'font-weight': 'bold'
                }
            },
            // 边样式
            {
                selector: 'edge',
                style: {
                    'width': 'mapData(strength, 0, 1, 1, 5)',
                    'line-color': '#95a5a6',
                    'target-arrow-color': '#95a5a6',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10,
                    'color': '#7f8c8d',
                    'text-background-color': '#fff',
                    'text-background-opacity': 0.8,
                    'text-background-padding': '3px'
                }
            },
            // 高亮样式
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#f39c12',
                    'background-color': '#f39c12'
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#f39c12',
                    'target-arrow-color': '#f39c12',
                    'width': 4
                }
            },
            // 悬停样式
            {
                selector: 'node:active',
                style: {
                    'overlay-color': '#f39c12',
                    'overlay-padding': '10px',
                    'overlay-opacity': 0.3
                }
            }
        ];
    }

    /**
     * 添加交互事件
     */
    addInteractions() {
        if (!this.cy) return;

        // 点击节点事件
        this.cy.on('tap', 'node', (event) => {
            const node = event.target;
            const nodeData = node.data();

            // 触发自定义事件，传递节点数据
            const customEvent = new CustomEvent('nodeSelected', {
                detail: nodeData
            });
            document.dispatchEvent(customEvent);

            // 高亮相关节点和边
            this.highlightNeighborhood(node);
        });

        // 点击空白处取消高亮
        this.cy.on('tap', (event) => {
            if (event.target === this.cy) {
                this.resetHighlight();
            }
        });

        // 双击节点居中
        this.cy.on('dbltap', 'node', (event) => {
            const node = event.target;
            this.cy.animate({
                center: { eles: node },
                zoom: 2
            }, {
                duration: 500
            });
        });
    }

    /**
     * 高亮节点及其邻居
     * @param {Object} node - Cytoscape 节点对象
     */
    highlightNeighborhood(node) {
        // 重置所有样式
        this.cy.elements().removeClass('highlighted dimmed');

        // 获取邻居节点和连接边
        const neighborhood = node.neighborhood().add(node);

        // 高亮选中的节点和邻居
        neighborhood.addClass('highlighted');

        // 淡化其他元素
        this.cy.elements().not(neighborhood).addClass('dimmed');

        // 添加淡化样式
        this.cy.style()
            .selector('.dimmed')
            .style({
                'opacity': 0.3
            })
            .selector('.highlighted')
            .style({
                'opacity': 1
            })
            .update();
    }

    /**
     * 重置高亮
     */
    resetHighlight() {
        this.cy.elements().removeClass('highlighted dimmed');
        this.cy.style()
            .selector('node, edge')
            .style({
                'opacity': 1
            })
            .update();
    }

    /**
     * 更新图谱数据
     * @param {Object} graphData - 新的图谱数据
     */
    update(graphData) {
        if (!this.cy) {
            this.initialize(graphData);
            return;
        }

        const elements = this.convertToElements(graphData);
        this.cy.elements().remove();
        this.cy.add(elements);
        this.cy.layout({
            name: 'cose',
            idealEdgeLength: 100,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 30
        }).run();
    }

    /**
     * 适应视图
     */
    fit() {
        if (this.cy) {
            this.cy.fit(null, 50);
        }
    }

    /**
     * 重置视图
     */
    reset() {
        if (this.cy) {
            this.cy.reset();
        }
    }

    /**
     * 导出图片
     * @param {string} format - 图片格式 ('png' 或 'jpg')
     * @returns {string} Base64 编码的图片数据
     */
    exportImage(format = 'png') {
        if (!this.cy) return null;

        return this.cy.png({
            output: 'base64',
            bg: 'white',
            full: true,
            scale: 2
        });
    }

    /**
     * 销毁图谱
     */
    destroy() {
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }
    }
}
