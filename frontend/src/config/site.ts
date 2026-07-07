export const siteConfig = {
  name: "Nexora Technologies",
  description: "Enterprise-grade SaaS platform building AI Employees to automate businesses.",
  url: "https://nexora.tech",
  ogImage: "https://nexora.tech/og.png",
  links: {
    github: "https://github.com/Fastian1337/Nexora",
  },
  contact: {
    email: "fastian1337@gmail.com",
  },
  products: [
    { name: "HealthLink", description: "AI Receptionist and workflow automation for clinics." },
    { name: "SchoolAI", description: "Admission agent and parent support for educational institutions." },
    { name: "BusinessAI", description: "Custom internal operations automations." },
    { name: "GrowthAI", description: "Social media, campaign and content generation agent." },
  ],
};

export type SiteConfig = typeof siteConfig;
