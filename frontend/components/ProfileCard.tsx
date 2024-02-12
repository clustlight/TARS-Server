import React from 'react'
import { User } from '../types/tars'
import Link from 'next/link'
import Image from 'next/image'

type Props = {
  user: User
}

const ProfileCard = ({ user }: Props) => {
  const profileUrl = `https://twitcasting.tv/${user.screen_id}`
  const iconPlaceholder = 'https://twitcasting.tv/img/twitcas_guest1_64.jpg'

  return (
    <div className='space-y-1 rounded-xl border-2 border-amber-500 bg-white shadow-2xl max-lg:py-6 lg:py-4'>
      <div className='max-w mx-auto flex items-center justify-center space-x-2 py-3'>
        <Link href={profileUrl}>
          <Image
            src={user.profile_image ? user.profile_image : iconPlaceholder}
            alt={`${user.screen_id}'s icon`}
            height={45}
            width={45}
            className='rounded-3xl border-2 border-gray-500'
          />
        </Link>

        <Link href={profileUrl}>
          <div>
            <span className='block truncate text-base font-semibold sm:w-[120px] xl:w-[180px]'>
              {user.user_name}
            </span>
            <span className='block truncate text-sm text-gray-400 sm:w-[120px] xl:w-[180px]'>
              @{user.screen_id}
            </span>
          </div>
        </Link>
      </div>

      <div className='flex justify-center space-x-4'>
        <span>
          レベル <span className='font-semibold'>{user.level}</span>
        </span>
        <span>
          サポーター{' '}
          <span className='font-semibold'>
            {user.supporter_count ? user.supporter_count.toLocaleString() : ''}
          </span>
        </span>
      </div>
    </div>
  )
}

export default ProfileCard
