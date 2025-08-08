<script setup lang="ts">
import srText from './srText.vue';


interface Dialog {
  index: number;
  idx: number;
  text: string;
  speaker: string;
}
const props = defineProps({
  dialogList: {
    type: Array as () => Dialog[] | null,
    default: null,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  gender: {
    type: Number,
    default: 0,
  },
});
</script>
<template>
  <v-list v-if="props.dialogList" :disabled="disabled">
    <v-list-item
      v-for="item in props.dialogList"
      :key="item.index"
      class="pt-4"
    >
      <div class="mb-1">
        <sr-text
          class="name"
          :text="item.speaker ? item.speaker : '< Anonymous >'"
        />
        <span class="idx nowrap ml-4"> #{{ item.idx }}</span>
      </div>
      <div>
        <sr-text :text="item.text ? item.text : ''" :gender="gender" />
      </div>
    </v-list-item>
  </v-list>
  <v-alert v-else> No data </v-alert>
</template>
