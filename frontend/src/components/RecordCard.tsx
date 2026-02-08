import dayjs from 'dayjs'
import { Recording } from '../types/tars'

type Props = {
  recording: Recording
}

const RecordCard = ({ recording }: Props) => {
  const thumbnailUrl = `https://apiv2.twitcasting.tv/users/${recording.screen_id}/live/thumbnail?size=large&position=beginning`
  const liveUrl = `https://twitcasting.tv/${recording.screen_id}`

  return (
    <div className='mx-3 space-y-1 rounded-xl border-2 border-indigo-400 bg-slate-200 py-6 shadow-2xl'>
      <div className='flex justify-center'>
        <a href={liveUrl} rel='noreferrer' target='_blank'>
          <img
            src={thumbnailUrl}
            alt={`${recording.user_name}'s thumbnail`}
            height={300}
            width={200}
            className='rounded-xl'
            loading='lazy'
          />
        </a>
      </div>

      <div className='flex justify-center'>
        <a href={liveUrl} rel='noreferrer' target='_blank'>
          <div className='my-2 space-y-1'>
            <span className='mx-1 block font-semibold'>{recording.live_title}</span>
            <span className='mx-1 block'>
              {recording.live_subtitle ? recording.live_subtitle : '-----'}
            </span>
            <span className='mx-1 block text-sm font-light text-gray-600'>
              {dayjs.unix(recording.start_time).format('YYYY/MM/DD HH:mm:ss')} -{' '}
              {dayjs().diff(dayjs.unix(recording.start_time), 'minute')}分経過
            </span>
          </div>
        </a>
      </div>

      <div className='flex items-center justify-center space-x-2 py-3'>
        <a href={recording.profile_image} rel='noreferrer' target='_blank'>
          <img
            src={recording.profile_image}
            alt={`${recording.screen_id}'s icon`}
            height={45}
            width={45}
            className='rounded-3xl border-2 border-red-600 p-0.5'
            loading='lazy'
          />
        </a>

        <a href={liveUrl} rel='noreferrer' target='_blank'>
          <div className='w-[150px]'>
            <span className='block truncate text-base font-semibold'>{recording.user_name}</span>
            <span className='block truncate text-sm text-gray-400'>@{recording.screen_id}</span>
          </div>
        </a>
      </div>
    </div>
  )
}

export default RecordCard
