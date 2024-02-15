import dayjs from 'dayjs'
import RecordCard from '../components/RecordCard'
import { Recording, User } from '../types/tars'
import Head from 'next/head'
import { useEffect, useRef, useState } from 'react'
import ProfileCard from '../components/ProfileCard'

const getRecordings = async (endpoint: string) => {
  const response = await fetch(`${endpoint}/recordings`)
  const data = await response.json()

  return data.recordings as Recording[]
}

const startRecording = async (endpoint: string, screen_id: string) => {
  const response = await fetch(`${endpoint}/recordings/${screen_id}`, {
    method: 'POST'
  })
  const data = await response.json()

  return data as Recording
}

const stopRecording = async (endpoint: string, screen_id: string) => {
  const response = await fetch(`${endpoint}/recordings/${screen_id}`, {
    method: 'DELETE'
  })

  const data = await response.json()

  return data
}

const getUsers = async (endpoint: string) => {
  const response = await fetch(`${endpoint}/users`)
  const data = await response.json()

  return data.users as User[]
}

const addUser = async (endpoint: string, screen_id: string) => {
  const response = await fetch(`${endpoint}/subscriptions/${screen_id}`, {
    method: 'POST'
  })
  const data = await response.json()

  return data as User
}

const removeUser = async (endpoint: string, screen_id: string) => {
  const response = await fetch(`${endpoint}/subscriptions/${screen_id}`, {
    method: 'DELETE'
  })

  const data = await response.json()

  return data as User
}

export default function Home() {
  const [recordings, setRecordings] = useState<Recording[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [refresh, setRefresh] = useState<boolean>(false)
  const [updateAt, setUpdateAt] = useState<string>('---')

  const [endpoint, setEndpoint] = useState<string>('')

  const recordingInputRef = useRef<HTMLInputElement>(null)
  const userInputRef = useRef<HTMLInputElement>(null)

  const intervalInputRef = useRef<HTMLInputElement>(null)
  const [intervalSec, setIntervalSec] = useState<number>(30)

  useEffect(() => {
    if (endpoint === '') {
      setEndpoint(
        `${window.location.protocol}//${window.location.hostname}:${window.location.port}`
      )
    }
    setUpdateAt('----/--/-- --:--:--')
    getRecordings(endpoint).then(data => {
      setRecordings(data)
      setUpdateAt(dayjs().format('YYYY/MM/DD HH:mm:ss'))
    })

    getUsers(endpoint).then(data => {
      setUsers(data)
    })

    const interval = setInterval(() => {
      setRefresh(previous => !previous)
    }, intervalSec * 1000)
    return () => clearInterval(interval)
  }, [refresh, endpoint, intervalSec])

  return (
    <>
      <Head>
        <title>TARS-UI</title>
      </Head>

      <main className='mx-10 my-10 space-y-5'>
        <div className='flex justify-center'>
          <div className='w-fit items-center space-x-5 space-y-2 border-2 px-5 py-2 md:flex'>
            <div className='space-x-3'>
              <span>更新間隔 (秒)</span>
              <input
                type='text'
                ref={intervalInputRef}
                defaultValue='30'
                className='w-16 rounded-3xl border-2 border-indigo-200 bg-gray-100 px-5 py-0.5 outline-none focus:border-emerald-400'
              />
              <button
                className='rounded-2xl border-2 border-violet-400 px-4 py-1.5'
                onClick={() => {
                  const data: number = Number(intervalInputRef.current?.value)
                    ? Number(intervalInputRef.current?.value)
                    : 30
                  setIntervalSec(data)
                }}
              >
                設定
              </button>
            </div>
            <span className='inline-block font-medium'>最終更新: {updateAt}</span>
          </div>
        </div>

        <div className='items-center py-5 max-lg:space-y-5 xl:flex xl:justify-between'>
          <h3 className='font-bold xl:text-xl'>・録画タスク ({recordings?.length})</h3>
          <div className='flex justify-center text-center'>
            <div className='justify-center md:flex md:space-x-5'>
              <input
                type='text'
                ref={recordingInputRef}
                className='my-5 rounded-3xl border-2 border-indigo-200 bg-gray-100 px-5 py-0.5 outline-none focus:border-emerald-400'
              />
              <div className='flex items-center justify-center space-x-4'>
                <button
                  className='my-5 rounded-2xl border-2 border-blue-400 px-4 py-1.5'
                  onClick={() => {
                    startRecording(endpoint, recordingInputRef.current?.value as string).then(() => setRefresh(previous => !previous))
                  }}
                >
                  開始
                </button>
                <button
                  className='my-5 rounded-2xl border-2 border-red-400 px-4 py-1.5'
                  onClick={() => {
                    stopRecording(endpoint, recordingInputRef.current?.value as string).then(() => setRefresh(previous => !previous))
                  }}
                >
                  終了
                </button>
                <button
                  className='my-5 rounded-2xl border-2 border-violet-400 px-4 py-1.5'
                  onClick={() => setRefresh(previous => !previous)}
                >
                  更新
                </button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className='grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-10 xl:grid-cols-5 xl:gap-10'>
            {recordings &&
              recordings.map(recording => (
                <RecordCard key={recording.live_id} recording={recording} />
              ))}
          </div>
        </div>

        <div className='items-center py-5 max-lg:space-y-5 xl:flex xl:justify-between'>
          <h3 className='font-bold xl:text-xl'>・自動録画対象 ({users?.length})</h3>
          <div className='flex justify-center text-center'>
            <div className='md:flex md:space-x-5'>
              <input
                type='text'
                ref={userInputRef}
                className='my-5 rounded-3xl border-2 border-indigo-200 bg-gray-100 px-5 py-0.5 outline-none focus:border-emerald-400'
              />
              <div className='flex items-center justify-center space-x-4'>
                <button
                  className='my-5 rounded-2xl border-2 border-blue-400 px-4 py-1.5'
                  onClick={() => {
                    addUser(endpoint, userInputRef.current?.value as string).then(() => setRefresh(previous => !previous))

                  }}
                >
                  追加
                </button>
                <button
                  className='my-5 rounded-2xl border-2 border-red-400 px-4 py-1.5'
                  onClick={() => {
                    removeUser(endpoint, userInputRef.current?.value as string).then(() => setRefresh(previous => !previous))
                  }}
                >
                  削除
                </button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className='grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-10 xl:grid-cols-5 xl:gap-x-14'>
            {users && users.map(user => <ProfileCard key={user.user_id} user={user} />)}
          </div>
        </div>
      </main>
    </>
  )
}
