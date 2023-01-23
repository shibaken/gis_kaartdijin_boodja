import { computed, ref, Ref } from "vue";

export interface ValidationConfig<T> {
  fields: Array<keyof T>
}

export interface MappingValidationError {
  category: string;
  id: string;
  description: string;
}
type FieldFilth<T> = {
  [Property in keyof T]: boolean;
}

export function getValidationRules<T>(config: ValidationConfig<T>) {
  function checkMandatoryFields (target: Partial<T>) {
    return config.fields
      .filter(field => target[field] === null || typeof target[field] === "undefined")
      .map(field => ({
        category: 'Mandatory',
        id: field,
        description: `Mandatory field '${field.toString()}' was empty`
      }));
  }

  return [
    checkMandatoryFields
  ]
}

export function useComputedValidation<T> (config: ValidationConfig<T>, target: Ref<Partial<T> | undefined>) {
  const validators = getValidationRules<T>(config);

  const validationErrors = computed(() => validators.flatMap(validator => validator(target.value ?? {})));

  const filthMap: FieldFilth<T> = Object.fromEntries(config.fields
    .map(field => [field, false])) as FieldFilth<T>;
  const dirtyFields = ref(filthMap);

  function enfilthenField (fieldName: keyof T) {
    dirtyFields.value = { ...dirtyFields.value, [fieldName]: true };
  }

  function cleanField (fieldName: keyof T) {
    dirtyFields.value = { ...dirtyFields.value, [fieldName]: false };
  }

  return { validationErrors, dirtyFields, enfilthenField, cleanField }
}