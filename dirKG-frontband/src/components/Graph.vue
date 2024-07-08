<script setup type="module">
  // 导入我们自己定义的axios.js文件,而不是导入axios依赖  
  import request from '../utils/request.js'
  import { onMounted,ref,reactive,toRaw } from 'vue';
 
  
      const entity = ref('');

      const submit = () => {
          const api_endpoint = "";
          request.post("api", { entity: entity.value })
              .then(response => {
                  console.log("Calling " + api_endpoint + " for " + entity.value);
                  const nodes = response.data.nodes;
                  const relationships = response.data.relationships;
                  nodes.forEach(node => {
                      node.Depth = parseInt(node.Depth.replace(/"/g, ''), 10);
                  });

                  console.log(nodes);
                  console.log(relationships);
                  renderNetwork(nodes, relationships);
              })
              .catch(err => console.log(err));
      };


      function renderNetwork(nodes, links) {
            d3.select("#svg1").selectAll("*").remove();
            let svg = d3.select("svg");
            var width = +svg.attr('width');
            var height = +svg.attr('height');
            let circles, lines, texts, linetexts;
            let simulation;
            var dragging = false;
            // const nodeIndexSet = new Set(nodes.map(node => node.id));
            // const links = relationships.filter(link => nodeIndexSet.has(link.source) && nodeIndexSet.has(link.target));
            
            const info = nodes.reduce((acc, node) => {
                acc[node.id] = {
                    "id":node.id,
                    "Label": node.Label,
                    "Name": node.Name,
                    "Parent":node.Parent,
                    "Route":node.Route,
                    "time": node.Creation_time,
                    "Depth": node.Depth,
                    "Content": node.Content
                };
                return acc;
            }, {});
           

            const zoom = d3.zoom()
                .scaleExtent([0.1, 10]) // Define the zoom scale limits
                .on('zoom', zoomed);
            svg.call(zoom); // Apply zoom behavior to the SVG

            // Create a group that will contain all nodes and links
            const mainsvg = svg.append('g');

            color = d3.scaleSequential(d3.interpolateRainbow)
                .domain([0, d3.max(nodes, d => d.Depth)]);

            function zoomed(event) {
                mainsvg.attr('transform', event.transform);
            }

            const render_init = function () {
                mainsvg.append("defs").append("marker")
                    .attr("id", "arrow")
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 12)  // 确保箭头在直线末端
                    .attr("markerWidth", 10)
                    .attr("markerHeight", 10)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("d", "M0,-5L10,0L0,5")
                    .attr("fill", "white");  // 设置箭头颜色

                lines = mainsvg.append('g')
                    .attr('class', 'lines')
                    .selectAll('line').data(links).join('line')
                    .attr('stroke-width', 1)
                    .attr('opacity', 1)  //设置透明度 0-1
                    .attr('marker-end', 'url(#arrow)');

                // Add text to each line
                linetexts = mainsvg.append('g')
                    .attr('class', 'linetexts')
                    .selectAll('text').data(links).join('text')
                    .text(d => d.relation)
                    .attr('font-size', 30)
                    .attr('opacity', 0); //设置透明度 0-1

                circles = mainsvg.append('g')
                    .attr('class', 'circles')
                    .selectAll('circle').data(nodes).join('circle')
                    .attr('r', d => (d3.max(nodes, d => d.Depth) - d.Depth + 1) * 6)
                    .attr('title', '节点')
                    .attr('fill', d => color(d.Depth))
                    .attr('name', d => d.Name)
                    .attr('id', d => d.id)
                    .on('mouseover', mouseover_circles)
                    .on('mouseout', mouseout_circles)
                    .call(d3.drag()
                        .on('start', dragstarted)
                        .on('drag', dragged)
                        .on('end', dragended));

                texts = mainsvg.append('g')
                    .attr('class', 'texts')
                    .selectAll('text').data(nodes).join('text')
                    .attr('fill', d => color(d.Depth))
                    .attr('name', d => d.Name)
                    .attr('font-size', d => (d3.max(nodes, d => d.Depth) - d.Depth + 1) * 10)
                    .text(d => d.Name)
                    .attr('id', d => d.id)
                    .on('mouseover', mouseover_texts)
                    .on('mouseout', mouseout_texts)
                    .call(d3.drag()
                        .on('start', dragstarted)
                        .on('drag', dragged)
                        .on('end', dragended));
            }
         

            function ticked() {
                // 使用 requestAnimationFrame 优化动画效果，确保每一帧只渲染一次，减少重复渲染。
                window.requestAnimationFrame(() => {
                    // lines.attr('x1', d => d.source.x)
                    //    .attr('y1', d => d.source.y)
                    //    .attr('x2', d => d.target.x)
                    //    .attr('y2', d => d.target.y)

                    lines.attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => {
                            const radius = (d3.max(nodes, d => d.Depth) - d.target.Depth + 1) * 6;
                            const dx = d.target.x - d.source.x;
                            const dy = d.target.y - d.source.y;
                            const length = Math.sqrt(dx * dx + dy * dy);
                            const scale = (length - radius) / length;
                            return d.source.x + dx * scale;
                        })
                        .attr('y2', d => {
                            const radius = (d3.max(nodes, d => d.Depth) - d.target.Depth + 1) * 6;
                            const dx = d.target.x - d.source.x;
                            const dy = d.target.y - d.source.y;
                            const length = Math.sqrt(dx * dx + dy * dy);
                            const scale = (length - radius) / length;
                            return d.source.y + dy * scale;
                        });

                    // Update text position to the middle of each line
                    linetexts.attr('x', d => (d.source.x + d.target.x) / 2)
                        .attr('y', d => (d.source.y + d.target.y) / 2);

                    circles.attr('cx', d => d.x)
                        .attr('cy', d => d.y);

                    texts.attr('x', d => d.x)
                        .attr('y', d => d.y);
                });
            }

            function tdistance(link) {
                return Math.random() * 100 + 50;
            }

            // Define the drag functions
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
                dragging = true;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
                dragging = false;
            }

            // Define the mouseover function to show node info and filter neighbors
            function mouseover_circles(event, d) {
                if (!dragging) {
                    var name = d3.select(this).attr('Name');
                    var id = String(d3.select(this).attr('id'));

                    $('#info h4').css('color',d3.select(this).attr('fill')).text(name);
                    $('#info p').remove();
                    //展示ner.json里面的内容
                    
                    if (typeof(info[id]) != "undefined") {
                        for (var key in info[id]) {
                            var value = info[id][key]
                            // var flag_none = false;
                            // for (var item in value) {
                            //    if (value[item] == null || value[item] == 'N/A' || value[item] == '') {
                            //       flag_none = true;
                            //       break;
                            //    }
                            // } 
                            // if (flag_none == true) {              // 排除为空的属性值
                            //    continue;
                            // }

                            $('#info').append('<p><span>' + key + ':</span> ' + info[id][key] + '</p>');
                            
                        }
                    }

                // Highlight the selected node and its neighbors
                const neighbors = links.filter(link => link.source.id === d.id|| link.target.id === d.id);
                const neighborNodes = neighbors.map(link => link.source.id === d.id ? link.target : link.source);

                // Hide all lines and circles
                lines.style('opacity', 0);
                circles.style('opacity', 0);
                linetexts.style('opacity', 0);

                // Highlight the selected node and its neighbors
                circles.filter(node => node.id === d.id || neighborNodes.includes(node))
                    .style('opacity', 1);

                lines.filter(link => link.source.id === d.id || link.target.id === d.id)
                    .style('opacity', 1); //opacity 0-1

                linetexts.filter(link => link.source.id === d.id || link.target.id === d.id)
                    .style('opacity', 1);
                }
            }

            // Define the mouseout function to reset the view
            function mouseout_circles(event, d) {
                if (!dragging) {
                    // Reset the opacity of all lines and circles
                    lines.style('opacity', 0.8);
                    circles.style('opacity', 1);
                    linetexts.style('opacity', 0);
                }
            }

            function mouseover_texts(event, d) {
                if (!dragging) {

                    var name = d3.select(this).attr('Name');
                    var id = String(d3.select(this).attr('id'));

                    $('#info h4').css('color',d3.select(this).attr('fill')).text(name);
                    $('#info p').remove();
                    //展示ner.json里面的内容
                    
                    if (typeof(info[id]) != "undefined") {
                        for (var key in info[id]) {
                            var value = info[id][key]
                            // var flag_none = false;
                            // for (var item in value) {
                            //    if (value[item] == null || value[item] == 'N/A' || value[item] == '') {
                            //       flag_none = true;
                            //       break;
                            //    }
                            // } 
                            // if (flag_none == true) {              // 排除为空的属性值
                            //    continue;
                            // }

                            $('#info').append('<p><span>' + key + ':</span> ' + info[id][key] + '</p>');
                            
                        }
                    }
                    // Highlight the selected node and its neighbors
                    const neighbors = links.filter(link => link.source.id === d.id || link.target.id === d.id);
                    const neighborNodes = neighbors.map(link => link.source.id=== d.id ? link.target : link.source);

                    // Hide all lines and circles
                    lines.style('opacity', 0);
                    texts.style('opacity', 0);
                    linetexts.style('opacity', 0);

                    // Highlight the selected node and its neighbors
                    texts.filter(node => node.id === d.id || neighborNodes.includes(node)
                    ).style('opacity', 1);

                    lines.filter(link => link.source.id === d.id || link.target.id === d.id)
                        .style('opacity', 1); //opacity 0-1

                    linetexts.filter(link => link.source.id === d.id || link.target.id === d.id)
                        .style('opacity', 1);
                }
            }

            function mouseout_texts(event, d) {
                if (!dragging) {
                    // Reset the opacity of all lines and text
                    lines.style('opacity', 0.8);
                    texts.style('opacity', 1);
                    linetexts.style('opacity', 0);
                }
            }

            render_init();
            simulation = d3.forceSimulation(nodes)
                .force('manyBody', d3.forceManyBody().strength(-30))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force("link", d3.forceLink(links).id(d => d.id).strength(0.1).distance(tdistance))
                .on('tick', ticked);
        }

  
</script>

<template>
    <div>
     <!-- 实体输入框 -->
     <div id="entityInput">
         <h3 >请输入实体：</h3>
         <input type="text" autocomplete="off" class="form-control"  @keyup.enter="submit" v-model="entity">
     </div>

     <svg width="1080" height="700" id="svg1" class="svgs"
         style="display: block; margin: 0 auto; border: 1px solid transparent;"></svg>

     <!-- 每个结点的信息 -->
     <div id="info">
         <h4></h4>
    </div>
    </div>
   
</template>

<style scoped>
/* 引入css/graph.css样式 */
@import "../../public/css/graph.css"
</style>