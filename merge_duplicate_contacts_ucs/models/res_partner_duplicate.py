from odoo import models, fields, tools, _
import logging

_logger = logging.getLogger(__name__)

class ResPartnerDuplicate(models.Model):
    _name = 'res.partner.duplicate'
    _description = 'Duplicate Contact'
    _auto = False
    _order = 'duplicate_count desc, name asc'

    duplicate_by = fields.Selection([
        ('name', 'Name'),
        ('email', 'Email'),
    ], string='Duplicate Reason', readonly=True)
    name = fields.Char(string='Name', readonly=True)
    email = fields.Char(string='Email', readonly=True)
    type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Invoice Address'),
        ('delivery', 'Delivery Address'),
        ('other', 'Other Address'),
        ("private", "Private Address"),
    ], string='Address Type', readonly=True)
    is_company = fields.Boolean(string='Is a Company', readonly=True)
    duplicate_count = fields.Integer(string='Duplicate Count', readonly=True)
    duplicate_ids = fields.Char(string='Duplicate IDs', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW res_partner_duplicate AS (
                WITH duplicate_groups AS (
                    -- Group by Name
                    SELECT
                        'name' AS duplicate_by,
                        min(name) AS name,
                        string_agg(DISTINCT email, ', ') AS email,
                        type AS type,
                        is_company AS is_company,
                        count(*) AS duplicate_count,
                        string_agg(id::text, ', ') AS duplicate_ids
                    FROM
                        res_partner
                    WHERE
                        active = true
                        AND name IS NOT NULL AND name != ''
                    GROUP BY
                        lower(name), type, is_company
                    HAVING
                        count(*) > 1

                    UNION ALL

                    SELECT
                        'email' AS duplicate_by,
                        string_agg(DISTINCT name, ', ') AS name,
                        min(email) AS email,
                        type AS type,
                        is_company AS is_company,
                        count(*) AS duplicate_count,
                        string_agg(id::text, ', ') AS duplicate_ids
                    FROM
                        res_partner
                    WHERE
                        active = true
                        AND email IS NOT NULL AND email != ''
                    GROUP BY
                        lower(email), type, is_company
                    HAVING
                        count(*) > 1
                )
                SELECT
                    row_number() OVER () AS id,
                    duplicate_by,
                    name,
                    email,
                    type,
                    is_company,
                    duplicate_count,
                    duplicate_ids
                FROM
                    duplicate_groups
            )
        """)

    def action_view_partners(self):
        self.ensure_one()
        if not self.duplicate_ids:
            return False
        partner_ids = [int(x.strip()) for x in self.duplicate_ids.split(',') if x.strip()]
        return {
            'name': _('Duplicate Partners: %s') % (self.name or self.email),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('id', 'in', partner_ids)],
            'target': 'current',
        }

    def action_merge_duplicates(self):
        for record in self:
            if not record.duplicate_ids:
                continue
            partner_ids = [int(x.strip()) for x in record.duplicate_ids.split(',') if x.strip()]
            self._merge_partner_group(partner_ids)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _merge_partner_group(self, partner_ids):
        if len(partner_ids) < 2:
            return

        wizard_model = self.env['base.partner.merge.automatic.wizard']
        ordered_partners = wizard_model._get_ordered_partner(partner_ids)
        if not ordered_partners:
            return
        dst_partner = ordered_partners[-1]
        other_partners = ordered_partners[:-1]

        wizard = wizard_model.create({})

        chunk_size = 2
        for i in range(0, len(other_partners), chunk_size):
            chunk = other_partners[i:i + chunk_size]
            partners_to_merge = chunk | dst_partner
            wizard._merge(partners_to_merge.ids, dst_partner=dst_partner, extra_checks=False)
