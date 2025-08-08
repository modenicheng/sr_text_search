<script setup lang="ts">
const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  gender: {
    type: Number,
    required: false,
  },
  highlight: {
    type: String,
    required: false,
    default: ""
  }
});

const renderText = (text: string) => {
  text = text.replace(
    /<unbreak>(.*?)<\/unbreak>/g,
    '<span class="nowrap">$1</span>'
  );
  text = text.replace(/<break>/g, "<br \>");
  text = text.replace(/<b>(.*?)<\/b>/g, "<strong>$1</strong>");
  text = text.replace(
    /<color=#([0-9a-fA-F]{6,8})>(.*?)<\/color>/g,
    "<span style='color:#$1'>$2</span>"
  );
  text = text.replace(/<i>(.*?)<\/i>/g, "<em>$1</em>");
  text = text.replace(/<u>(.*?)<\/u>/g, "<u>$1</u>");
  text = text.replace(
    /{RUBY_B#(.*?)}(.*?){RUBY_E#}/g,
    `
    <ruby>
      $2<rt>$1</rt>
    </ruby>
    `
  );
  text = text.replace(
    /<size=([0-9]*?)>(.*?)<\/size>/g,
    "<span style='font-size:$1px'>$2</span>"
  );
  if (props.gender === 0) {
    text = text.replace(/{F#(.*?)}/g, "$1");
    text = text.replace(/{M#(.*?)}/g, "");
  } else {
    text = text.replace(/{M#(.*?)}/g, "$1");
    text = text.replace(/{F#(.*?)}/g, "");
  }

  text = text.replace(props.highlight, `<mark>${props.highlight}</mark>`)

  return text;
};
</script>
<template>
  <span v-html="renderText(props.text)"></span>
</template>

<style>
ruby rt {
  font-size: 65%;
  line-height: 0;
}

.nowrap {
  white-space: nowrap;
}
</style>
