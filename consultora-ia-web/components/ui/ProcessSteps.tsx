'use client'

import { motion } from 'framer-motion'
import { type LucideIcon } from 'lucide-react'

interface Step {
  number: number
  icon: LucideIcon
  title: string
  description: string
}

interface ProcessStepsProps {
  steps: Step[]
}

export default function ProcessSteps({ steps }: ProcessStepsProps) {
  return (
    <div className="relative">
      {/* Connecting line — desktop only */}
      <div className="hidden lg:block absolute top-10 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-200 to-transparent z-0" />

      <div className="relative z-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
        {steps.map((step, index) => {
          const Icon = step.icon
          return (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: index * 0.12 }}
              className="relative flex flex-col items-center text-center"
            >
              {/* Number (large, background) */}
              <div className="relative mb-5">
                {/* Large number watermark */}
                <span className="absolute -top-4 -left-3 text-6xl font-black text-blue-50 select-none leading-none z-0">
                  {step.number}
                </span>
                {/* Icon circle */}
                <div className="relative z-10 flex items-center justify-center w-16 h-16 bg-white border-2 border-blue-100 rounded-2xl shadow-sm group-hover:border-blue-300 transition-colors">
                  <Icon className="w-7 h-7 text-blue-600" />
                </div>
              </div>

              {/* Step number badge */}
              <div className="inline-flex items-center justify-center w-6 h-6 bg-blue-600 text-white text-xs font-bold rounded-full mb-3">
                {step.number}
              </div>

              {/* Content */}
              <h3 className="text-base font-semibold text-gray-900 mb-2 leading-snug">{step.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{step.description}</p>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
