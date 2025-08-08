<script setup lang="ts">
import axios from "axios";
import { computed, ref } from "vue";
import srText from "./components/srText.vue";
const api = axios.create({
  baseURL: "/api",
});

const speakerQuery = ref([]);
const speakers = ref([]);
const speakerLoading = ref(false);
const getSpeakers = (
  query: string[],
  offset: number = 0,
  limit: number = 200
) => {
  speakerLoading.value = true;
  if (query.length === 0) {
    speakers.value = [];
    speakerLoading.value = false;
    return;
  }
  api
    .get("/speakers/", {
      params: {
        query,
        offset,
        limit,
      },
    })
    .then((res) => {
      // speakers.value = res.data.data.map((item: string) => {
      //   return { name: item };
      // });
      speakers.value = res.data.data;
      speakerLoading.value = false;
    })
    .catch(() => {
      speakerLoading.value = false;
    });
};

interface Dialog {
  index: number;
  idx: number;
  text: string;
  speaker: string;
}

const dialogParams = ref<{
  limit: number;
  pageNumber: number;
  context: boolean;
  idx: number | undefined;
}>({
  limit: 20,
  pageNumber: 1,
  context: false,
  idx: undefined,
});

const keywordQuery = ref<[]>();
const keywordSearch = ref();
const dialogLoading = ref(false);
const dialog = ref<Dialog[]>();
const dialogTotal = ref(0);
const dialogOffset = computed(() => {
  return (dialogParams.value.pageNumber - 1) * dialogParams.value.limit;
});
const dialogSpeakers = computed(() => {
  return speakerQuery.value.join("//");
});
const dialogKeywords = computed(() => {
  return keywordQuery.value?.join("//");
});
const getDialog = () => {
  dialogLoading.value = true;
  api
    .get("/dialog/", {
      params: {
        speakers: dialogSpeakers.value,
        text: dialogKeywords.value,
        offset: dialogOffset.value,
        limit: dialogParams.value.limit,
        context: dialogParams.value.context,
        idx: dialogParams.value.idx ? dialogParams.value.idx : null,
      },
    })
    .then((res) => {
      dialog.value = res.data.data;
      dialogLoading.value = false;
      dialogTotal.value = res.data.total;
    })
    .catch(() => {
      dialogLoading.value = false;
    });
};

const speakerSearch = ref();
const gender = ref(0);
// 0 = f
// 1 = m
getDialog();
</script>
<template>
  <v-responsive class="border rounded">
    <v-app>
      <!-- <v-app-bar title="App bar"></v-app-bar> -->
      <v-main>
        <v-container>
          <v-card class="pa-4 mt-4">
            <v-form>
              <v-row class="ga-4 pa-3">
                <v-col>
                  <v-autocomplete
                    auto-select-first
                    clearbale
                    variant="solo"
                    multiple
                    v-model="speakerQuery"
                    v-model:search="speakerSearch"
                    :items="speakers"
                    @update:search="
                      (value) => {
                        getSpeakers(value);
                      }
                    "
                    @update:model-value="
                      () => {
                        speakerSearch = '';

                        dialogParams.pageNumber = 1;
                        getDialog();
                      }
                    "
                    :loading="speakerLoading"
                    label="说话人 / Speaker"
                  >
                    <template v-slot:chip="{ props, item }">
                      <v-chip
                        v-bind="props"
                        :color="`grey-lighten-1`"
                        size="small"
                        variant="flat"
                        closable
                        label
                      >
                        <sr-text :text="item.value" />
                      </v-chip>
                    </template>
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props" v-bind:title="''">
                        <v-list-item-title>
                          <sr-text :text="item.value" />
                        </v-list-item-title>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                  <v-combobox
                    clearbale
                    variant="solo"
                    multiple
                    :no-filter="true"
                    v-model="keywordQuery"
                    v-model:search="keywordSearch"
                    @update:model-value="
                      () => {
                        keywordSearch = '';
                        dialogParams.pageNumber = 1;
                        getDialog();
                      }
                    "
                    :loading="speakerLoading"
                    label="台词关键词 / Keywords"
                  >
                    <template v-slot:chip="{ props, item }">
                      <v-chip
                        v-bind="props"
                        :color="`grey-lighten-1`"
                        size="small"
                        variant="flat"
                        closable
                        label
                      >
                        {{ item.value }}
                      </v-chip>
                    </template>
                  </v-combobox>
                </v-col>
                <v-col>
                  <v-text-field
                    variant="solo"
                    type="number"
                    clearable
                    density="compact"
                    v-model="dialogParams.idx"
                    label="台词索引 / Index"
                    @update:model-value="getDialog"
                    @click:clear="
                      dialogParams.idx = undefined;
                      dialogParams.context = false;
                      getDialog();
                    "
                  />
                  <v-btn
                    block
                    @click="gender === 0 ? (gender = 1) : (gender = 0)"
                    >载体名称：{{ gender === 0 ? "星" : "穹" }}</v-btn
                  >
                  <v-checkbox
                    v-model="dialogParams.context"
                    label="上下文 / Context"
                  ></v-checkbox>
                </v-col>
              </v-row>
            </v-form>
          </v-card>
          <v-card class="pa-4 mt-4">
            <v-row> </v-row>
            <v-list v-if="dialog" :disabled="dialogLoading">
              <v-list-item
                v-for="item in dialog"
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
                  <sr-text
                    :text="item.text ? item.text : ''"
                    :gender="gender"
                    @click="
                      () => {
                        dialogParams.idx = item.idx;
                        dialogParams.context = true;
                        getDialog();
                      }
                    "
                  />
                </div>
              </v-list-item>
            </v-list>
            <v-alert v-else> No data </v-alert>
            <v-container>
              <v-row justify="space-around">
                <v-spacer />
                <v-text-field
                  style="height: 100%; margin-top: 5px"
                  label="页码 / Page"
                  variant="outlined"
                  v-model="dialogParams.pageNumber"
                  :min-width="130"
                  :max-width="130"
                  density="compact"
                  hide-details="auto"
                  type="number"
                  @update:model-value="getDialog"
                />

                <v-pagination
                  v-model="dialogParams.pageNumber"
                  :length="Math.ceil(dialogTotal / dialogParams.limit)"
                  :total-visible="7"
                  size="small"
                  @update:model-value="getDialog"
                  :disabled="dialogLoading"
                />

                <v-select
                  style="height: 100%; margin-top: 5px"
                  :items="[10, 20, 30, 40, 50, 100, 150, 200, 300]"
                  hide-details="auto"
                  v-model="dialogParams.limit"
                  :min-width="130"
                  :max-width="130"
                  density="compact"
                  variant="outlined"
                  label="每页条数 / Limit"
                  @update:model-value="getDialog"
                />
                <v-spacer />
              </v-row>
            </v-container>
          </v-card>
        </v-container>
      </v-main>
    </v-app>
  </v-responsive>
</template>
<style>
ruby rt {
  font-size: 65%;
  line-height: 0;
}

.name {
  font-weight: bold;
  font-size: 1.2rem;
}

.idx {
  font-size: 0.8rem;
  opacity: 0.5;
}

.nowrap {
  white-space: nowrap;
}
</style>
