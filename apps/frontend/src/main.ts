import './assets/css/main.css';
import 'vue-sonner/style.css';

import { createPinia } from 'pinia';
import { createApp } from 'vue';
import VueFeather from 'vue-feather';
import Icon from '@/components/ui/Icon.vue';
import PageHeaderVue from '@/components/ui/PageHeader.vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

app.component(VueFeather.name, VueFeather);
app.component('PageHeader', PageHeaderVue);
app.component('Icon', Icon);
app.use(createPinia());
app.use(router);

app.mount('#app');
