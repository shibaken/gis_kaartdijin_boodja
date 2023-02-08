import { computed, ref, Ref } from "vue";

export interface ValidationConfig<T> {
  mandatory?: Array<keyof T>,
  oneOf?: Array<[keyof T, keyof T]>,
  isInteger?: Array<keyof T>
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
  function checkMandatoryFields (target: Partial<T>): Array<MappingValidationError> {
    const fields = config.mandatory ?? [];
    return fields.filter(field => !target[field])
      .map(field => ({
        category: 'Mandatory',
        id: field,
        description: `Mandatory field '${field.toString()}' was empty`
      } as MappingValidationError));
  }

  function oneOf (target: Partial<T>) {
    const fields = config.oneOf ?? [];
    return fields.filter(([first, second]) => !target[first] && !target[second])
      .map(([first, second]) => ({
        category: 'One of',
        id: `${first.toString()}-${second.toString()}`,
        description: `One field is required: '${first.toString()}' '${second.toString()}'`
      } as MappingValidationError)) ?? [];
  }

  function isInteger (target: Partial<T>) {
    const fields = config.isInteger ?? [];
    return fields.filter(field => !Number.isInteger(target[field]))
      .map(field => ({
        category: 'Is integer',
        id: field,
        description: `Field must be an integer: '${field.toString()}'`
      } as MappingValidationError));
  }

  return [
    checkMandatoryFields,
    oneOf,
    isInteger
  ]
}

export function useComputedValidation<T> (config: ValidationConfig<T>, target: Ref<Partial<T> | undefined>) {
  const validators = getValidationRules<T>(config);
  const validationErrors = computed(() => validators.flatMap(validator => validator(target.value ?? {})));

  // Get a list of all validating fields
  const filthMap: FieldFilth<T> = Object.fromEntries(
    [config.mandatory ?? [], config.oneOf?.flat() ?? [], config.isInteger ?? []]
      .flat()
      .filter((value: keyof T, index: number, self: Array<keyof T>) => self.indexOf(value) === index)
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