import './assets/css/main.css';
import 'vue-sonner/style.css';

import { createPinia } from 'pinia';
import { createApp } from 'vue';
import Icon from '@/components/ui/Icon.vue';
import Loader from '@/components/ui/Loader.vue';
import PageHeaderVue from '@/components/ui/PageHeader.vue';
import Skeleton from '@/components/ui/Skeleton.vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

app.component('PageHeader', PageHeaderVue);
app.component('Icon', Icon);
app.component('Loader', Loader);
app.component('Skeleton', Skeleton);
app.use(createPinia());
app.use(router);

app.mount('#app');
