import React from 'react'
import { getInitials, getAvatarColor } from '../../../utils/formatters'
import type { AvatarColor } from '../../../types'
import styles from './Avatar.module.css'

type AvatarSize = 'xs' | 'sm' | 'md' | 'lg'

interface AvatarProps {
  name: string
  color?: AvatarColor
  size?: AvatarSize
  className?: string
}

export function Avatar({ name, color, size = 'md', className = '' }: AvatarProps) {
  const resolvedColor = color ?? getAvatarColor(name)
  return (
    <span
      className={[styles.avatar, styles[size], `av-${resolvedColor}`, className].join(' ').trim()}
      title={name}
      aria-label={name}
    >
      {getInitials(name)}
    </span>
  )
}
