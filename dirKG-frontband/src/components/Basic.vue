<script setup>
import { ref, onMounted } from 'vue';


// 使用 ref 创建响应式变量
const modeSpans = ref([]);
const searchInput = ref(null);

// 处理模式点击事件
const handleModeClick = (event) => {
  modeSpans.value.forEach(span => span.classList.remove('active'));
  event.target.classList.add('active');

  if (event.target.textContent === 'Circles') {
    d3.selectAll('.texts text').style('display', 'none');
    d3.selectAll('.circles circle').style('display', 'block');
  } else {
    d3.selectAll('.texts text').style('display', 'block');
    d3.selectAll('.circles circle').style('display', 'none');
  }
};

// 处理搜索框事件
const handleSearchKeyUp = (event) => {
  const name = event.target.value;
  const isActive = (d) => d.Name.toLowerCase().includes(name.toLowerCase()) ? '' : 'inactive';

  if (name === '') {
    d3.selectAll('#svg1 .texts text, #svg1 .circles circle, #svg1 .lines line, #svg1 #arrow')
      .attr('class', '');
    d3.selectAll('#svg1 .linetexts text')
      .attr('fill-opacity', 0);
  } else {
    d3.selectAll('#svg1 .circles circle, #svg1 .texts text')
      .attr('class', isActive);
    d3.selectAll('#svg1 .lines line')
      .attr('class', 'inactive');
    d3.selectAll('#svg1 .linetexts text')
      .attr('fill-opacity', 0);
    d3.selectAll('#svg1 #arrow')
      .attr('class', 'inactive');
  }
};

// 使用 onMounted 钩子来初始化事件监听器
onMounted(() => {
  modeSpans.value = document.querySelectorAll('#mode span');
  modeSpans.value.forEach(span => span.addEventListener('click', handleModeClick));

  if (searchInput.value) {
    searchInput.value.addEventListener('keyup', handleSearchKeyUp);
  }
});
</script>

<template>
  <div>
    <!-- 模式 -->
    <div id="mode">
      <span class="active" style="border-top-right-radius: 0; border-bottom-right-radius: 0;">Circles</span>
      <span style="border-top-left-radius: 0; border-bottom-left-radius: 0; position: relative; left: -5px;">Texts</span>
    </div>

    <!-- 搜索框 -->
    <div id="search">
      <input type="text" autocomplete="off" class="form-control" ref="searchInput">
    </div>

    <svg width="1080" height="700" id="svg1" class="svgs"
         style="display: block; margin: 0 auto; border: 1px solid transparent;"></svg>
  </div>
</template>

<style scoped>
/* 引入 css/graph.css 的样式 */
@import "../../public/css/graph.css";
</style>
