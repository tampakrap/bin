#!/usr/bin/ruby

require 'colored'
require 'puppet_forge'
require 'r10k/puppetfile'

if ARGV[0]
  puppetfile_path = ARGV[0]
else
  puppetfile_path = '/etc/puppet/environments/production'
end

puppetfile = R10K::Puppetfile.new(puppetfile_path).load
user_agent = 'Tampakrap/0.1.0'

modules = {}

puppetfile.each do |pup_mod|
  if pup_mod.class == R10K::Module::Forge

    forge_version = PuppetForge::Module.find(pup_mod.title.gsub('/', '-')).current_release.version

    modules[pup_mod.title] = [pup_mod.expected_version, forge_version]

    if pup_mod.expected_version == forge_version
      puts "#{pup_mod.title} is up to date"
    else
      puts "#{pup_mod.title} is OUTDATED: #{pup_mod.expected_version} vs #{forge_version}".red
    end
  end
end
