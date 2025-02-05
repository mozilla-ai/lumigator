import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import LPageHeader from '../molecules/LPageHeader.vue'

describe('LPageHeader', () => {
  it('renders properly', () => {
    const wrapper = mount(LPageHeader, { props: { msg: 'Hello Vitest' } })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})
