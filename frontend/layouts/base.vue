<template>
  <a-layout class="layout">
    <a-layout-header>
      <a-row type="flex" justify="space-between">
        <a-avatar
          size="large"
          style="margin: 12px 0"
          :src="require('~/static/logo.jpg')"
        />
        <a-menu
          theme="dark"
          mode="horizontal"
          :selected-keys="[$nuxt.$route.name]"
          :style="{ lineHeight: '64px' }"
        >
          <a-menu-item key="index">
            <nuxt-link :to="{ name: 'index'}" />Main
          </a-menu-item>
          <a-menu-item key="projects">
            <nuxt-link :to="{ name: 'projects'}" />Projects
          </a-menu-item>
        </a-menu>
      </a-row>
    </a-layout-header>
    <a-layout-content style="padding: 24px; min-height: 100%">
      <Nuxt />
    </a-layout-content>
    <a-layout-footer style="text-align: center">
      Audio annotation tool by <a href="https://t.me/ruslantau">ruslantau</a>
    </a-layout-footer>
  </a-layout>
</template>

<script>
export default {
  name: 'IndexPage'
}
</script>

<style>
#components-layout-demo-top .logo {
  width: 120px;
  height: 31px;
  background: rgba(255, 255, 255, 0.2);
  margin: 16px 24px 16px 0;
  float: left;
}
</style>
