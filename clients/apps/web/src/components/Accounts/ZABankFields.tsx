'use client'

import Input from '@polar-sh/ui/components/atoms/Input'
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@polar-sh/ui/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@polar-sh/ui/components/ui/select'
import { useFormContext } from 'react-hook-form'
import type { BankFormValues } from './PaystackBankAccountForm'

export default function ZABankFields() {
  const { control } = useFormContext<BankFormValues>()

  return (
    <>
      <FormField
        control={control}
        name="account_name"
        rules={{ required: 'Account name is required' }}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Account Holder Name</FormLabel>
            <FormControl>
              <Input {...field} placeholder="Ann Bron" />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="account_type"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Account Type</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select account type" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="personal">Personal</SelectItem>
                <SelectItem value="business">Business</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="document_type"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Identity Document Type</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select document type" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="identityNumber">Identity Number</SelectItem>
                <SelectItem value="passportNumber">Passport Number</SelectItem>
                <SelectItem value="businessRegistrationNumber">
                  Business Registration Number
                </SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="document_number"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Document Number</FormLabel>
            <FormControl>
              <Input {...field} placeholder="1234567890123" />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  )
}
