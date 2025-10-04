#!/usr/bin/env node

/**
 * ACTA Hackathon Submission Verification Script
 * 
 * This script verifies that your submission meets all requirements
 * and helps ensure you won't be flagged for anti-cheating violations.
 * 
 * Run before submitting: node verify-submission.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Hackathon timing (CET timezone)
const HACKATHON_START = new Date('2025-10-04T12:00:00+02:00'); // Oct 4, 12:00 CET
const HACKATHON_END = new Date('2025-10-05T12:00:00+02:00');   // Oct 5, 12:00 CET

const MINIMUM_COMMITS = 5;
const INITIAL_TIMESTAMP_FILE = '.hackathon-start';

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function header(message) {
  log(`\n${'='.repeat(60)}`, colors.bright);
  log(message, colors.bright + colors.blue);
  log('='.repeat(60), colors.bright);
}

function checkmark(passed, message) {
  const symbol = passed ? '✅' : '❌';
  const color = passed ? colors.green : colors.red;
  log(`${symbol} ${message}`, color);
  return passed;
}

function warning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

function getGitCommits() {
  try {
    const output = execSync('git log --pretty=format:"%H|%aI|%s"', { encoding: 'utf-8' });
    return output.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const [hash, date, message] = line.split('|');
        return {
          hash,
          date: new Date(date),
          message
        };
      })
      .filter(commit => commit.message !== 'acta-hackathon-setup') // Exclude setup commit
      .reverse(); // Chronological order
  } catch (error) {
    return [];
  }
}

function checkInitialTimestamp() {
  header('Checking Initial Timestamp');
  
  const timestampPath = path.join(process.cwd(), INITIAL_TIMESTAMP_FILE);
  const exists = fs.existsSync(timestampPath);
  
  if (!checkmark(exists, `Initial timestamp file (${INITIAL_TIMESTAMP_FILE}) exists`)) {
    log('\n  Create it now with:', colors.yellow);
    log(`  date > ${INITIAL_TIMESTAMP_FILE}`, colors.yellow);
    log(`  git add ${INITIAL_TIMESTAMP_FILE}`, colors.yellow);
    log(`  git commit -m "🎯 Starting ACTA Hackathon - $(date)"`, colors.yellow);
    return false;
  }
  
  try {
    const content = fs.readFileSync(timestampPath, 'utf-8');
    log(`\n  Timestamp content: ${content.trim()}`, colors.blue);
  } catch (error) {
    warning('Could not read timestamp file content');
  }
  
  return true;
}

function checkCommitTiming(commits) {
  header('Checking Commit Timing');
  
  if (commits.length === 0) {
    checkmark(false, 'Found commits in repository');
    log('\n  Make sure you have committed your code!', colors.yellow);
    log('  (Note: "acta-hackathon-setup" commit is excluded from checks)', colors.blue);
    return false;
  }
  
  checkmark(true, `Found ${commits.length} participant commits`);
  
  const firstCommit = commits[0];
  const lastCommit = commits[commits.length - 1];
  
  log(`\n  First commit: ${firstCommit.date.toISOString()}`, colors.blue);
  log(`  Last commit:  ${lastCommit.date.toISOString()}`, colors.blue);
  
  const startedOnTime = firstCommit.date >= HACKATHON_START;
  const finishedOnTime = lastCommit.date <= HACKATHON_END;
  
  checkmark(
    startedOnTime,
    `First commit after hackathon start (Oct 4, 12:00 CET)`
  );
  
  if (!startedOnTime) {
    const diff = Math.abs(firstCommit.date - HACKATHON_START) / 1000 / 60;
    warning(`First commit was ${diff.toFixed(0)} minutes too early!`);
  }
  
  checkmark(
    finishedOnTime,
    `Last commit before deadline (Oct 5, 12:00 CET)`
  );
  
  if (!finishedOnTime) {
    const diff = (lastCommit.date - HACKATHON_END) / 1000 / 60;
    warning(`Last commit was ${diff.toFixed(0)} minutes too late!`);
  }
  
  return startedOnTime && finishedOnTime;
}

function checkCommitFrequency(commits) {
  header('Checking Commit Frequency');
  
  // Filter to only commits during the hackathon window
  const validCommits = commits.filter(c => 
    c.date >= HACKATHON_START && c.date <= HACKATHON_END
  );
  
  checkmark(
    validCommits.length >= MINIMUM_COMMITS,
    `At least ${MINIMUM_COMMITS} commits during hackathon (found ${validCommits.length})`
  );
  
  if (validCommits.length < MINIMUM_COMMITS) {
    warning(`Make more commits! You need ${MINIMUM_COMMITS - validCommits.length} more.`);
    return false;
  }
  
  // Check commit distribution
  const timeSpan = HACKATHON_END - HACKATHON_START;
  const quarterSpan = timeSpan / 4;
  
  const quarters = [0, 1, 2, 3].map(q => {
    const start = new Date(HACKATHON_START.getTime() + q * quarterSpan);
    const end = new Date(HACKATHON_START.getTime() + (q + 1) * quarterSpan);
    return validCommits.filter(c => c.date >= start && c.date < end).length;
  });
  
  const emptyQuarters = quarters.filter(c => c === 0).length;
  
  if (emptyQuarters <= 1) {
    checkmark(true, 'Commits well distributed throughout hackathon');
  } else {
    warning('Commits are bunched together - this may look suspicious');
    log('  Consider committing more regularly throughout the event', colors.yellow);
  }
  
  // Check for suspicious single massive commit
  if (validCommits.length === 1) {
    warning('Only 1 commit found - this will likely be flagged!');
    log('  Make multiple commits as you build features', colors.yellow);
    return false;
  }
  
  return true;
}

function checkCommitMessages(commits) {
  header('Checking Commit Messages');
  
  // Only check commits during the hackathon window
  const validCommits = commits.filter(c => 
    c.date >= HACKATHON_START && c.date <= HACKATHON_END
  );
  
  if (validCommits.length === 0) {
    warning('No commits found during hackathon window');
    return false;
  }
  
  const poorMessages = validCommits.filter(c => 
    c.message.length < 5 || 
    /^(wip|fix|update|stuff|temp|test)$/i.test(c.message.trim())
  );
  
  if (poorMessages.length > validCommits.length / 2) {
    warning('Many commits have poor quality messages');
    log('  Good commit messages help demonstrate your progress', colors.yellow);
  } else {
    checkmark(true, 'Commit messages look reasonable');
  }
  
  log('\n  Hackathon commits:', colors.blue);
  validCommits.slice(-5).forEach(c => {
    log(`    ${c.date.toLocaleString('en-US', { timeZone: 'Europe/Paris' })} - ${c.message}`, colors.reset);
  });
  
  return true;
}

function checkGitHistory() {
  header('Checking Git History Integrity');
  
  try {
    // Check for force pushes or history rewrites
    execSync('git reflog --all', { encoding: 'utf-8' });
    checkmark(true, 'Git history appears intact');
    
    // Check for suspicious operations
    const reflog = execSync('git reflog', { encoding: 'utf-8' });
    const hasRebase = reflog.includes('rebase');
    const hasReset = reflog.includes('reset');
    
    if (hasRebase || hasReset) {
      warning('Detected rebase or reset operations');
      log('  If you had a good reason, be prepared to explain this', colors.yellow);
    }
    
    return true;
  } catch (error) {
    warning('Could not verify git history');
    return false;
  }
}

function checkProjectFiles() {
  header('Checking Project Files');
  
  const hasReadme = fs.existsSync('README.md');
  checkmark(hasReadme, 'README.md exists');
  
  if (hasReadme) {
    const readme = fs.readFileSync('README.md', 'utf-8');
    const hasProjectInfo = readme.length > 1000 && !readme.includes('[SUBMISSION LINK TO BE ADDED]');
    
    if (hasProjectInfo) {
      checkmark(true, 'README appears to be updated with project info');
    } else {
      warning('README might still be the template');
      log('  Update it with your project description!', colors.yellow);
    }
  }
  
  // Check for common project files
  const files = fs.readdirSync(process.cwd());
  const hasCode = files.some(f => 
    f.endsWith('.js') || 
    f.endsWith('.ts') || 
    f.endsWith('.py') || 
    f.endsWith('.html') ||
    ['src', 'app', 'lib', 'pages'].includes(f)
  );
  
  checkmark(hasCode, 'Project code files detected');
  
  return hasReadme && hasCode;
}

function generateReport(results) {
  header('VERIFICATION REPORT');
  
  const allPassed = Object.values(results).every(v => v);
  
  if (allPassed) {
    log('\n🎉 All checks passed! Your submission looks good.', colors.green + colors.bright);
    log('\n📋 SUBMISSION REQUIREMENTS:', colors.blue + colors.bright);
    log('Before submitting via https://forms.acta.so/r/wMobdM, ensure you have:', colors.blue);
    log('');
    log('  1. ✅ Public GitHub repository URL', colors.green);
    log('  2. ✅ 60-second demo video (Loom, YouTube) - MUST BE PUBLIC', colors.green);
    log('  3. ✅ Live public demo URL (deployed app)', colors.green);
    log('  4. ✅ Your email address', colors.green);
    log('  5. ✅ Your name', colors.green);
    log('');
    log('⚠️  CRITICAL: All links must be PUBLIC and working!', colors.yellow + colors.bright);
    log('   - Test your GitHub repo in an incognito window');
    log('   - Watch your video to ensure it plays publicly');
    log('   - Open your deployed app in incognito to verify it works');
    log('');
    log('📝 Next steps:', colors.blue);
    log('1. Deploy your app (see DEPLOYMENT_GUIDE.md)');
    log('2. Record your 60s demo video');
    log('3. Make GitHub repo PUBLIC (Settings → Change visibility)');
    log('4. Test all links in incognito/private browsing');
    log('5. Submit: https://forms.acta.so/r/wMobdM');
    log('6. Join Discord for winner announcements');
  } else {
    log('\n⚠️  Some checks failed. Please fix the issues above.', colors.red + colors.bright);
    log('\nFailed checks:', colors.red);
    Object.entries(results).forEach(([check, passed]) => {
      if (!passed) {
        log(`  ❌ ${check}`, colors.red);
      }
    });
  }
  
  log('\n' + '='.repeat(60), colors.bright);
  log('🏆 Submission: https://forms.acta.so/r/wMobdM', colors.magenta + colors.bright);
  log('❓ Questions? Discord or DM @acta.so on Instagram', colors.blue);
  log('='.repeat(60) + '\n', colors.bright);
  
  return allPassed;
}

// Main execution
function main() {
  log('\n');
  log('  █████╗  ██████╗████████╗ █████╗     ██╗  ██╗ █████╗  ██████╗██╗  ██╗', colors.magenta);
  log(' ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝', colors.magenta);
  log(' ███████║██║        ██║   ███████║    ███████║███████║██║     █████╔╝ ', colors.magenta);
  log(' ██╔══██║██║        ██║   ██╔══██║    ██╔══██║██╔══██║██║     ██╔═██╗ ', colors.magenta);
  log(' ██║  ██║╚██████╗   ██║   ██║  ██║    ██║  ██║██║  ██║╚██████╗██║  ██╗', colors.magenta);
  log(' ╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝', colors.magenta);
  log('\n           Submission Verification Tool - 24h Hackathon\n', colors.bright);
  
  const commits = getGitCommits();
  
  const results = {
    'Initial Timestamp': checkInitialTimestamp(),
    'Commit Timing': checkCommitTiming(commits),
    'Commit Frequency': checkCommitFrequency(commits),
    'Commit Messages': checkCommitMessages(commits),
    'Git History': checkGitHistory(),
    'Project Files': checkProjectFiles()
  };
  
  const allPassed = generateReport(results);
  
  process.exit(allPassed ? 0 : 1);
}

// Check if git is available
try {
  execSync('git --version', { encoding: 'utf-8' });
  main();
} catch (error) {
  log('❌ Git is not installed or not available', colors.red);
  log('   Please install Git and ensure this is a Git repository', colors.yellow);
  process.exit(1);
}
