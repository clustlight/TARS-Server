(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[405],{8312:function(e,s,r){(window.__NEXT_P=window.__NEXT_P||[]).push(["/",function(){return r(7028)}])},7028:function(e,s,r){"use strict";r.r(s),r.d(s,{default:function(){return f}});var n=r(5893),t=r(7484),l=r.n(t),a=r(5675),c=r.n(a),i=r(1664),d=r.n(i),o=r(7294);let x=e=>{let{recording:s}=e,r="https://apiv2.twitcasting.tv/users/".concat(s.screen_id,"/live/thumbnail?size=large&position=latest"),t="https://twitcasting.tv/".concat(s.screen_id);return(0,n.jsxs)("div",{className:"mx-3 space-y-1 rounded-xl border-2 border-indigo-400 bg-slate-200 py-6 shadow-2xl",children:[(0,n.jsx)("div",{className:"flex justify-center",children:(0,n.jsx)(d(),{href:t,children:(0,n.jsx)(c(),{src:r,alt:"".concat(s.user_name,"'s thumbnail"),height:300,width:200,priority:!0,className:"rounded-xl"})})}),(0,n.jsx)("div",{className:"flex justify-center",children:(0,n.jsx)(d(),{href:t,children:(0,n.jsxs)("div",{className:"my-2 space-y-1",children:[(0,n.jsx)("span",{className:"mx-1 block font-semibold",children:s.live_title}),(0,n.jsx)("span",{className:"mx-1 block",children:s.live_subtitle?s.live_subtitle:"null"}),(0,n.jsxs)("span",{className:"mx-1 block text-sm font-light text-gray-600",children:[l().unix(s.start_time).format("YYYY/MM/DD HH:mm:ss")," -"," ",l()().diff(l().unix(s.start_time),"minute"),"分経過"]})]})})}),(0,n.jsxs)("div",{className:"flex items-center justify-center space-x-2 py-3",children:[(0,n.jsx)(d(),{href:s.profile_image,children:(0,n.jsx)(c(),{src:s.profile_image,alt:"".concat(s.screen_id,"'s icon"),height:45,width:45,className:"rounded-3xl border-2 border-red-600 p-0.5"})}),(0,n.jsx)(d(),{href:t,children:(0,n.jsxs)("div",{className:"w-[150px]",children:[(0,n.jsx)("span",{className:"block truncate text-base font-semibold",children:s.user_name}),(0,n.jsxs)("span",{className:"block truncate text-sm text-gray-400",children:["@",s.screen_id]})]})})]})]})};var u=r(9008),m=r.n(u);let h=async e=>{let s=await fetch("".concat(e,"/recordings")),r=await s.json();return r.recordings},p=async(e,s)=>{let r=await fetch("".concat(e,"/recordings/").concat(s),{method:"POST"}),n=await r.json();return n},b=async(e,s)=>{let r=await fetch("".concat(e,"/recordings/").concat(s),{method:"DELETE"}),n=await r.json();return n};function f(){let[e,s]=(0,o.useState)([]),[r,t]=(0,o.useState)(!1),[a,c]=(0,o.useState)("---"),[i,d]=(0,o.useState)(""),u=(0,o.useRef)(null),f=(0,o.useRef)(null),[j,v]=(0,o.useState)(30);return(0,o.useEffect)(()=>{""===i&&d("http://".concat(window.location.hostname,":").concat(window.location.port)),c("----/--/-- --:--:--"),h(i).then(e=>{s(e),c(l()().format("YYYY/MM/DD HH:mm:ss"))});let e=setInterval(()=>{t(e=>!e)},1e3*j);return()=>clearInterval(e)},[r,i,j]),(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(m(),{children:(0,n.jsx)("title",{children:"TARS-UI"})}),(0,n.jsxs)("main",{className:"mx-10 my-10 space-y-10",children:[(0,n.jsxs)("div",{className:"flex w-1/2 items-center space-x-5 border-2 px-5 py-2",children:[(0,n.jsx)("span",{children:"更新間隔 (秒)"}),(0,n.jsx)("input",{type:"text",ref:f,defaultValue:"30",className:"w-16 rounded-3xl border-2 border-indigo-200 bg-gray-100 px-5 py-0.5 outline-none focus:border-emerald-400"}),(0,n.jsx)("button",{className:"rounded-2xl border-2 border-violet-400 px-4 py-1.5",onClick:()=>{var e,s;let r=Number(null===(e=f.current)||void 0===e?void 0:e.value)?Number(null===(s=f.current)||void 0===s?void 0:s.value):30;v(r)},children:"設定"}),(0,n.jsxs)("span",{className:"font-medium",children:["最終更新: ",a]})]}),(0,n.jsxs)("div",{className:"flex space-x-4 py-5",children:[(0,n.jsxs)("h3",{className:"text-xl font-bold",children:["・録画タスク (",null==e?void 0:e.length,")"]}),(0,n.jsxs)("div",{className:"space-x-5",children:[(0,n.jsx)("input",{type:"text",ref:u,className:"rounded-3xl border-2 border-indigo-200 bg-gray-100 px-5 py-0.5 outline-none focus:border-emerald-400"}),(0,n.jsx)("button",{className:"rounded-2xl border-2 border-blue-400 px-4 py-1.5",onClick:()=>{var e;p(i,null===(e=u.current)||void 0===e?void 0:e.value),t(e=>!e)},children:"開始"}),(0,n.jsx)("button",{className:"rounded-2xl border-2 border-red-400 px-4 py-1.5",onClick:()=>{var e;b(i,null===(e=u.current)||void 0===e?void 0:e.value),t(e=>!e)},children:"終了"}),(0,n.jsx)("button",{className:"rounded-2xl border-2 border-violet-400 px-4 py-1.5",onClick:()=>t(e=>!e),children:"更新"})]})]}),(0,n.jsx)("div",{children:(0,n.jsx)("div",{className:"grid grid-cols-5 gap-2 md:grid-cols-6 md:gap-10",children:e&&e.map(e=>(0,n.jsx)(x,{recording:e},e.live_id))})}),(0,n.jsxs)("div",{className:"flex space-x-4 py-5",children:[(0,n.jsx)("h3",{className:"text-xl font-bold",children:"・自動録画対象 (未実装)"}),(0,n.jsxs)("div",{className:"space-x-5",children:[(0,n.jsx)("input",{type:"text",className:"rounded-3xl border-2 border-indigo-200 bg-gray-100 px-5 py-0.5 outline-none focus:border-emerald-400"}),(0,n.jsx)("button",{className:"rounded-2xl border-2 border-blue-400 px-4 py-1.5",children:"追加"}),(0,n.jsx)("button",{className:"rounded-2xl border-2 border-red-400 px-4 py-1.5",children:"削除"})]})]})]})]})}}},function(e){e.O(0,[459,774,888,179],function(){return e(e.s=8312)}),_N_E=e.O()}]);