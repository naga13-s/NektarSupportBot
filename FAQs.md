FAQs
Activities
* With which account or opportunity would an activity be linked?

 Nektar uses proprietary affinity models to determine this. See Graph inference for more information.

* An activity is missing in Salesforce. Why?

   1. Activities matching read screening rules are not stored or processed by Nektar, and any that match write screening rules are not written to Salesforce. Verify that no Data controls match the missing activity.
   2. Nektar only capture activities where if at least one of the participants is an existing Salesforce lead or contact, or whose email address has the same domain as an existing contact or account. Verify that the missing activity links to an existing Salesforce record.
   3. Calendar events more than 3 months into the future are not processed by Nektar until they come within the 3 month window.
   4. The activity might be in the processing pipeline. See Sync latency for expected time duration.
   * To look up what happened to a specific activity, use Tracker.

   * Do Google Calendar and MS365 Calendar event updates sync to Salesforce?

 Yes, Nektar treats Google/MS365 calendars as the main source of truth. Any changes to the meeting title, date, time, participants, or description will sync back to Salesforce. However, if an internal user has made updates to the event in Salesforce, Nektar will not override those changes, respecting the user's decisions. For more details, see Self healing.

   * How does Nektar handle activities that occurred before the account was created in Salesforce?

 When the account is created and gets a domain name (from the “website” field or a contact), all the people with matching email addresses and their conversations will be created on Salesforce. This is part of the Nektar self-healing feature.

   * The activity creation date has changed since it was originally created. Why?

 Salesforce does not reliably handle certain updates to activities, such as re-associating it from a contact to a lead. In rare situations, Nektar has to delete and recreate the activity because of the new information it becomes aware of. For more details, see Self healing.

   * Why is Nektar creating old activities now?

 Nektar can be configured with a start date, and only activities that occurred after that date will be captured.

However, note that Nektar captures activities when it becomes convinced of its relevance to your sales process, which may not be when the activities actually happen. For example, an old activity may be skipped initially, and captured later when a Salesforce account is created with the same domain name as one of its participants’ email addresses. For more details, see Self healing.

   * Does Nektar create duplicate activities in Salesforce?

 Nektar does not create duplicate activities. However, Nektar does not de-duplicate against other activity capture systems that may be running on the same users. To ensure that no activities are duplicated, disable other activity capture tools for Nektar users.

   * An activity has both leads and contacts as participants. Who will Nektar create this activity with?

 Nektar prioritizes contacts over leads. Nektar will link an activity with a lead only if there are neither existing contacts nor activity participants that can be created as contacts.

   * An activity has participants from multiple domains. Where will Nektar create this activity?

 Nektar creates this activity with the best suited Account or Opportunity. We use our proprietary affinity models to do this. See Graph inference for more information.

   * How long does it take for Nektar to write activities in Salesforce?

 Nektar checks Google or MS365 every 10 minutes and connects with Salesforce APIs every 20 minutes, writing up to 200 records per API call. However, there may be occasional delays in fetching and writing activities. See Sync latency for more information.

   * Why do I see duplicate records when I pull activity reports on Salesforce?

 This is because shared activities has been turned on in your Salesforce. In shared activities, when internal Salesforce users are added as participants, Salesforce creates a copy of the event for each internal user. On the account or opportunity, you will see only the parent event. However, when pulling reports, all copies of the event will be visible. To avoid inflated counts, all past and future reports using activities should set "Event invitations" to false, ensuring activities are not counted multiple times.

   * Why is an activity linked to an account even when there are open opportunities under that account?

 Nektar’s affinity models find the best opportunity or account for each activity. When there are multiple opportunities and there is ambiguity about which one the activity relates to, Nektar adds it to the account instead.

If this is happening frequently, you may wish to review your policies around opportunity and opportunity-contact role creation policies to ensure that there is an unambiguous opportunity where each conversation belongs.

   * Why are activities assigned to users whose inboxes and calendars Nektar is not reading?

 Nektar can only access the inboxes and calendars of Nektar users. However, it may assign emails or events to other Salesforce users if the algorithm determines that they are a more appropriate owner. See Owner for more information.

   * How does Nektar decide who should be the activity owner?

 See Owner

Contacts
      * With which account and opportunities would a contact be linked?

 Nektar creates contacts under the account with a domain name that matches the contact’s email address. An account’s domain name may come from its “Website” field, or be inferred from the email addresses of other contacts already in it.

Nektar considers a person related to an opportunity if he/she has participated in an activity related to that opportunity. By default, all buyers related to an opportunity are linked to that opportunity using OCRs, but this can be overridden using write rules.

      * Does Nektar create duplicate contacts on Salesforce?

 Nektar will not create a contact when it knows of an existing contact or lead with the same email address. However, it may create a duplicate if it is unaware of the existing record. This might happen when:

         1. The existing contact or lead was created within the last 20 minutes
         2. The integration user’s permissions prevent Nektar from seeing the existing contact or lead
         3. A duplicate lead or contact was created manually after Nektar created a contact.
         * In all these situations, as soon as Nektar becomes aware of the existence of a duplicate, it will resolve it by deleting the contact it created, and transferring all the activities and fields to the surviving contact or lead. See Self healing for more information.

         * How does Nektar handle contacts whose conversations occurred before the account was created on Salesforce?

 With Nektar’s time travel feature, once you have created account and added website, all the people matching to that domain will be created as contacts and conversations done with them will be linked to the account.

         * I created some contacts on Salesforce. If found, will Nektar update details on these contacts like title, phone number, etc.?

 Yes, Nektar updates contacts no matter whether created by Nektar or users.

         * There are multiple internal people marked on an activity. How does Nektar decide who should be the contact owner?

 Contacts are associated with accounts. The owner of the Account with which the Contact was associated is assigned as the Contact owner. See Owner

Admin controls
            * How can I add or remove users?

 See Users

            * How can I stop Nektar capturing private calendar meetings?

 You can turn off private calendar meetings sync from blocking section under read rules.

            * What controls are available to prevent Nektar capturing sensitive information?

 Nektar has a robust set of read rules that you can use to define what Nektar should not read. For more details, see Data controls

            * Can I enable read and write of specific Salesforce objects, e.g. contacts without activities?

 Yes, Nektar offers the flexibility to enable read/write at an object level.

            * Can I see a log of all the activities and persons that Nektar read but did not create in Salesforce?

 No. The majority activity in your sellers’ inboxes and calendars are not external sales-related communications, and so Nektar does not write them into Salesforce. As the volume of such activities tends to be excessive and may contain sensitive or personal conversations, we do not provide any interface to review such activities manually.

If you have a specific activity to track down, use Tracker .

            * How do I switch a connector to a different integration user / admin user / service account?

 See the Connector documentation for Salesforce, Google Workspace, Microsoft 365 and Zoom.

Security
               * How does Nektar secure my data?

 Nektar offers the highest level of security to all customers. Nektar is compliant with SOC2 Type II, ISO 27001, and with GDPR (General Data Protection Regulation). For more details, see Security

               * What permissions are required by Nektar?

 See the Connector documentation for Salesforce, Google Workspace, Microsoft 365 and Zoom.

               * Why does Nektar need delete permissions on Salesforce?

 Nektar’s self-healing system re-evaluates past data capture decisions in light of new information, and where necessary reverts changes made by Nektar. Here are a couple of examples:

                  * Nektar might add a contact to a certain opportunity, but in light of later activities it may turn out that a different opportunity was a better fit for this person. In this case, Nektar will delete the first opportunity-contact role record and create a new one.
                  * Nektar might create a contact, but a user or tool might manually create a lead with the same email address. In this case, Nektar will delete the contact it created and re-associate all its data and activities to the manually created lead.
                  * At no point does Nektar delete any records that it did not originally create. Nektar will also not delete any records that were updated manually (or by other tools) after they were created.

                  * What custom fields are created by Nektar in Salesforce?

 See Nektar custom fields

                  * How do I know what data Nektar has created in Salesforce?

 You may review the Dashboard for overall statistics. To review specific contacts, activities and opportunity-contact roles, create a Salesforce report filtering on the “NektarActions__c” field.

                  * Which IP addresses does Nektar make API calls from?

 Nektar will make API calls to your Salesforce, Google, MS365 and other services from one of the following IP addresses: 44.207.41.98, 100.24.77.218, 44.206.28.70, 54.82.117.103.

                  * What is Nektar’s read (Google/MS365) and write (Salesforce) frequency?

 See Sync latency.

                  * How many Salesforce APIs does Nektar consume everyday?

 Nektar is very efficient in its Salesforce API consumption, and on an ongoing basis it consumes under 2,000 API calls (total) per day. For comparison, the Salesforce’s API quota is 100,000 + (number of licenses x calls per license type) + purchased API Call Add-Ons. For details, see Salesforce API limits.

                  * How many objects does Nektar writes per API call?

 Nektar writes data to Salesforce in batches of 200 objects at a time and continues writing until all the objects have been processed. On average, writing 200 objects takes about 10-30 seconds.

Salesforce provides generous API limits, which vary depending on the customer's Salesforce edition. You can review Salesforce API rate limits here.

                  * How does Nektar’s AI agent, Daisy, use and store customer data?

 Nektar's AI agent follows enterprise-grade security standards to ensure your data remains protected.

                     * Your data is processed through OpenAI, Google Gemini and AWS Bedrock APIs. All of these are SOC2 compliant.
                     * We have enterprise agreements in place that explicitly prohibit data storage or use for model training. For more details, you can review their terms of service here: OpenAI, Google, AWS.
                     * Nektar prioritizes data security and compliance, ensuring that your information is handled with the highest level of protection.