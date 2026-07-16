<template>
  <el-form :model="form" label-width="100px">
    <el-form-item label="图书编号"
      ><el-input v-model="form.isbn"
    /></el-form-item>
    <el-form-item label="图书名称"
      ><el-input v-model="form.name"
    /></el-form-item>
    <el-form-item label="价格"><el-input v-model="form.price" /></el-form-item>
    <el-form-item label="作者"><el-input v-model="form.author" /></el-form-item>
    <el-form-item label="出版社"
      ><el-input v-model="form.publisher"
    /></el-form-item>
    <el-form-item label="出版时间"
      ><el-date-picker
        v-model="form.createTime"
        value-format="YYYY-MM-DD"
        type="date"
        style="width: 100%"
    /></el-form-item>
    <el-form-item label="馆藏总数"
      ><el-input-number
        v-model="form.totalCount"
        :min="1"
        :max="999"
        :precision="0"
        style="width: 100%"
    /></el-form-item>
    <el-form-item v-if="editing" label="当前可借"
      ><el-input v-model="form.availableCount" disabled
    /></el-form-item>
  </el-form>
</template>
<script>
export default {
  name: "BookForm",
  props: {
    form: { type: Object, required: true },
    editing: { type: Boolean, default: false },
  },
};
</script>
