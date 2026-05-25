import { render } from '@react-email/render'
import { Command } from 'commander'

import emails from './emails'

const program = new Command()

program
  .description(
    'Render an email template to HTML. Props are read as JSON from stdin.',
  )
  .argument('<template>', 'name of the email template')
  .action(async (template: string) => {
    try {
      const chunks: Buffer[] = []
      for await (const chunk of process.stdin) {
        chunks.push(chunk as Buffer)
      }
      const props = Buffer.concat(chunks).toString('utf8')
      const parsedProps = JSON.parse(props)
      const TemplateComponent = emails[template]
      if (!TemplateComponent) {
        console.error(`Template ${template} not found`)
        process.exit(1)
      }
      const html = await render(<TemplateComponent {...parsedProps} />)
      console.log(html)
    } catch (error) {
      console.error('Error parsing JSON string:', error)
      process.exit(1)
    }
  })

program.parseAsync(process.argv)
