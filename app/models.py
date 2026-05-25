from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'category'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'


class Inventory(db.Model):
    id                    = db.Column(db.Integer, primary_key=True)
    expiry_date           = db.Column(db.Date, nullable=True)
    product_name          = db.Column(db.String(255), nullable=False)
    unit                  = db.Column(db.String(50))
    quantity              = db.Column(db.Integer, default=0)
    selling_price         = db.Column(db.Float)
    restock_threshold     = db.Column(db.Integer, default=5)
    undertaking_property  = db.Column(db.String(100), nullable=True)
    product_image         = db.Column(db.String(255), nullable=True)
    status                = db.Column(db.String(50), default='Active')
    is_deleted            = db.Column(db.Boolean, default=False)
    deleted_at            = db.Column(db.DateTime, nullable=True)

    history_logs = db.relationship(
        'DisposalHistory', backref='item', lazy=True, cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.Index('ix_inventory_deleted_status', 'is_deleted', 'status'),
        db.Index('ix_inventory_product_name', 'product_name'),
        db.Index('ix_inventory_expiry_date', 'expiry_date'),
        db.Index('ix_inventory_quantity', 'quantity'),
    )

    @property
    def balance(self):
        return self.quantity or 0

    @property
    def total(self):
        return (self.quantity or 0) * (self.selling_price or 0)

    @property
    def total_balance_amount(self):
        return self.total

    def __repr__(self):
        return f'<Inventory {self.id} - {self.product_name}>'

    def to_dict(self):
        return {
            'id':                   self.id,
            'expiry_date':          self.expiry_date.isoformat() if self.expiry_date else None,
            'product_name':         self.product_name,
            'unit':                 self.unit,
            'quantity':             self.quantity,
            'selling_price':        self.selling_price,
            'restock_threshold':    self.restock_threshold,
            'undertaking_property': self.undertaking_property,
            'product_image':        self.product_image,
            'status':               self.status,
        }


class DisposalHistory(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    inventory_id    = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    event_type      = db.Column(db.String(50))
    status_snapshot = db.Column(db.String(50))
    event_date      = db.Column(db.DateTime, default=datetime.now)
    remarks         = db.Column(db.String(255))
    quantity        = db.Column(db.Float, default=1.0)
    is_resolved     = db.Column(db.Boolean, default=False)

    __table_args__ = (
        # FK join and per-item history lookups
        db.Index('ix_disposal_history_inventory_id', 'inventory_id'),
        # Always ordered newest-first
        db.Index('ix_disposal_history_event_date', 'event_date'),
        # Filtered by event type (e.g. Disposal, Restoration)
        db.Index('ix_disposal_history_event_type', 'event_type'),
    )

    def __repr__(self):
        return f'<DisposalHistory {self.event_type} - {self.status_snapshot}>'


class User(UserMixin, db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(80),  unique=True, nullable=True)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    google_id      = db.Column(db.String(255), unique=True, nullable=True)
    password_hash  = db.Column(db.String(256), nullable=True)
    role           = db.Column(db.String(20),  default='user')
    oauth_provider = db.Column(db.String(20))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username or self.email}>'


class Borrowing(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    inventory_id  = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    quantity      = db.Column(db.Integer, nullable=False)
    status        = db.Column(db.String(50), default='Borrowed')
    date_borrowed = db.Column(db.DateTime, default=datetime.now)
    date_returned = db.Column(db.DateTime, nullable=True)
    item = db.relationship('Inventory', backref=db.backref('borrowings', lazy=True))

    __table_args__ = (
        # FK join to inventory
        db.Index('ix_borrowing_inventory_id', 'inventory_id'),
        # Filter active vs returned borrows
        db.Index('ix_borrowing_status', 'status'),
    )

    def __repr__(self):
        return f'<Borrowing {self.borrower_name} - {self.status}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id         = db.Column(db.Integer, primary_key=True)
    timestamp  = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user       = db.Column(db.String(100), nullable=False)
    action     = db.Column(db.String(100), nullable=False)
    target     = db.Column(db.String(255), nullable=True)
    details    = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(50),  nullable=True)

    __table_args__ = (
        # All audit queries order by timestamp desc
        db.Index('ix_audit_log_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user}>'


class POSTransaction(db.Model):
    __tablename__ = 'pos_transaction'
    id              = db.Column(db.Integer, primary_key=True)
    receipt_no      = db.Column(db.String(30), unique=True, nullable=False)  # unique → auto-indexed
    cashier         = db.Column(db.String(100), nullable=False)
    total_amount    = db.Column(db.Float, nullable=False, default=0.0)
    amount_tendered = db.Column(db.Float, nullable=True)
    change_given    = db.Column(db.Float, nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.now, nullable=False)

    items = db.relationship(
        'POSTransactionItem', backref='transaction', lazy=True, cascade='all, delete-orphan'
    )

    __table_args__ = (
        # Transaction list always ordered by created_at desc
        db.Index('ix_pos_transaction_created_at', 'created_at'),
    )

    def __repr__(self):
        return f'<POSTransaction {self.receipt_no}>'


class POSTransactionItem(db.Model):
    __tablename__ = 'pos_transaction_item'
    id             = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('pos_transaction.id'), nullable=False)
    inventory_id   = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=True)
    product_name   = db.Column(db.String(255), nullable=False)
    unit_price     = db.Column(db.Float, nullable=False)
    quantity       = db.Column(db.Integer, nullable=False)
    subtotal       = db.Column(db.Float, nullable=False)

    inventory = db.relationship('Inventory', backref=db.backref('pos_items', lazy=True))

    __table_args__ = (
        # FK join — every receipt detail lookup goes through transaction_id
        db.Index('ix_pos_transaction_item_transaction_id', 'transaction_id'),
        # FK join — reverse lookup from inventory to its sales history
        db.Index('ix_pos_transaction_item_inventory_id', 'inventory_id'),
    )

    def __repr__(self):
        return f'<POSItem {self.product_name} x{self.quantity}>'
