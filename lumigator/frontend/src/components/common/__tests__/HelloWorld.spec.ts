import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import LPageHeader from '@/components/layout/LPageHeader.vue'

describe('LPageHeader', () => {
  it('renders properly', () => {
    const wrapper = mount(LPageHeader, { props: { title: 'Hello Vitest' } })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})
