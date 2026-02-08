import dayjs from 'dayjs'
import { Recording } from '../types/tars'

type Props = {
  recording: Recording
}

const RecordCard = ({ recording }: Props) => {
  const thumbnailUrl = `https://apiv2.twitcasting.tv/users/${recording.screen_id}/live/thumbnail?size=large&position=beginning`
  const liveUrl = `https://twitcasting.tv/${recording.screen_id}`

  const formatElapsedTime = (startTime: number): string => {
    const minutes = dayjs().diff(dayjs.unix(startTime), 'minute')
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    const days = Math.floor(hours / 24)
    const hrs = hours % 24

    if (days > 0) {
      return `${days}日${hrs}時間`
    } else if (hours > 0) {
      return `${hours}時間${mins}分`
    } else {
      return `${minutes}分`
    }
  }

  return (
    <div className='group relative flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-md transition-all hover:border-blue-400 hover:shadow-xl dark:border-gray-700 dark:bg-gray-800 dark:hover:border-blue-500'>
      <div className='absolute right-3 top-3 z-10'>
        <span className='flex items-center space-x-1 rounded-full bg-gradient-to-r from-red-600 to-red-500 px-3 py-1 text-xs font-bold text-white shadow-lg'>
          <span className='h-1.5 w-1.5 animate-pulse rounded-full bg-white'></span>
          <span>LIVE</span>
        </span>
      </div>

      <div className='flex justify-center p-4'>
        <a href={liveUrl} rel='noreferrer' target='_blank'>
          <div className='relative overflow-hidden rounded-lg'>
            <div className='absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 transition-opacity group-hover:opacity-100'></div>
            <img
              src={thumbnailUrl}
              alt={`${recording.user_name}'s thumbnail`}
              className='h-auto w-full max-w-[200px] rounded-lg object-contain transition-transform group-hover:scale-105'
              loading='lazy'
            />
          </div>
        </a>
      </div>

      <div className='px-4 pb-3'>
        <a href={liveUrl} rel='noreferrer' target='_blank'>
          <div className='space-y-2.5 text-center'>
            <h3 className='truncate text-base font-bold text-gray-900 transition-colors group-hover:text-blue-600 dark:text-white dark:group-hover:text-blue-400'>
              {recording.live_title}
            </h3>
            {recording.live_subtitle && (
              <p className='truncate text-xs text-gray-600 dark:text-gray-400'>
                {recording.live_subtitle}
              </p>
            )}
            <div className='flex flex-wrap items-center justify-center gap-2 pt-1'>
              <div className='inline-flex items-center space-x-1.5 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'>
                <svg className='h-3 w-3' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
                  />
                </svg>
                <span>{formatElapsedTime(recording.start_time)}</span>
              </div>
              <div className='inline-flex items-center space-x-1.5 rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-300'>
                <svg className='h-3 w-3' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
                  />
                </svg>
                <span>{dayjs.unix(recording.start_time).format('MM/DD HH:mm')}</span>
              </div>
            </div>
          </div>
        </a>
      </div>

      <div className='mt-auto flex items-center space-x-3 border-t border-gray-100 bg-gradient-to-b from-gray-50 to-white px-4 py-3 dark:border-gray-700 dark:from-gray-800 dark:to-gray-800'>
        <a
          href={recording.profile_image}
          rel='noreferrer'
          target='_blank'
          className='flex-shrink-0'
        >
          <img
            src={recording.profile_image}
            alt={`${recording.screen_id}'s icon`}
            className='h-10 w-10 rounded-full border-2 border-red-400 object-cover shadow-sm'
            loading='lazy'
          />
        </a>

        <a href={liveUrl} rel='noreferrer' target='_blank' className='min-w-0 flex-1'>
          <div className='min-w-0'>
            <span className='block truncate text-sm font-bold text-gray-900 dark:text-white'>
              {recording.user_name}
            </span>
            <span className='block truncate text-xs text-gray-500 dark:text-gray-400'>
              @{recording.screen_id}
            </span>
          </div>
        </a>
      </div>
    </div>
  )
}

export default RecordCard
