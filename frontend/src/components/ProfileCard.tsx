import { User } from '../types/tars'

type Props = {
  user: User
}

const ProfileCard = ({ user }: Props) => {
  const profileUrl = `https://twitcasting.tv/${user.screen_id}`
  const iconPlaceholder = 'https://twitcasting.tv/img/twitcas_guest1_64.jpg'

  return (
    <div className='@container group overflow-hidden rounded-xl border border-gray-200 bg-white shadow-md transition-all hover:border-amber-400 hover:shadow-xl dark:border-gray-700 dark:bg-gray-800 dark:hover:border-amber-500'>
      <div className='mx-auto flex items-center space-x-3 px-4 py-5'>
        <a href={profileUrl} rel='noreferrer' target='_blank' className='flex-shrink-0'>
          <div className='relative'>
            <div className='absolute -inset-0.5 rounded-full bg-gradient-to-r from-red-500 to-red-400 opacity-0 blur transition-opacity group-hover:opacity-75'></div>
            <img
              src={user.profile_image ? user.profile_image : iconPlaceholder}
              alt={`${user.screen_id}'s icon`}
              className='relative h-14 w-14 flex-shrink-0 rounded-full border-2 border-white object-cover ring-2 ring-red-500 transition-all group-hover:ring-red-600'
              loading='lazy'
            />
          </div>
        </a>

        <a href={profileUrl} rel='noreferrer' target='_blank' className='min-w-0 flex-1'>
          <div className='min-w-0'>
            <span className='block truncate text-sm font-bold text-gray-900 transition-colors group-hover:text-amber-600 dark:text-white dark:group-hover:text-amber-400 @[200px]:text-base @[240px]:text-lg'>
              {user.user_name}
            </span>
            <span className='block truncate text-xs text-gray-500 dark:text-gray-400 @[240px]:text-sm'>
              @{user.screen_id}
            </span>
          </div>
        </a>
      </div>

      <div className='flex justify-around border-t border-gray-100 bg-gradient-to-b from-gray-50 to-white px-4 py-3 text-sm dark:border-gray-700 dark:from-gray-800 dark:to-gray-800'>
        <div className='flex items-center space-x-1.5'>
          <span className='text-xs text-gray-500 dark:text-gray-400'>レベル</span>
          <span className='font-bold text-amber-600 dark:text-amber-400'>{user.level}</span>
        </div>
        <div className='h-5 w-px bg-gray-200 dark:bg-gray-700'></div>
        <div className='flex items-center space-x-1.5'>
          <span className='text-xs text-gray-500 dark:text-gray-400'>サポーター</span>
          <span className='font-bold text-pink-600 dark:text-pink-400'>
            {user.supporter_count ? user.supporter_count.toLocaleString() : '0'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default ProfileCard
