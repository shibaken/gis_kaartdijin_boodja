import { mount } from '@vue/test-utils';
import CataloguePage from '../components/CataloguePage.vue';
import { createApp } from "vue";
import { createPinia, setActivePinia } from "pinia";

const app = createApp({})
beforeEach(() => {
  const pinia = createPinia();
  app.use(pinia);
  setActivePinia(pinia);
})

test('Mount component', async () => {
  expect(CataloguePage).toBeTruthy();

  const wrapper = mount(CataloguePage, {})

  expect(wrapper.get('.card-header > h4').text()).toContain('Layer Subscriptions');
  expect(wrapper.html()).toMatchSnapshot();
});
